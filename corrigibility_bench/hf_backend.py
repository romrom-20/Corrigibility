"""Single-GPU Hugging Face backend; heavy dependencies are imported only on load."""
from __future__ import annotations

from dataclasses import dataclass
import importlib.metadata
import os
import platform
import time

from .normative_hysteresis import digest


@dataclass
class Generation:
    raw_text: str
    rendered_prompt: str
    input_tokens: int
    output_tokens: int
    truncated: bool
    elapsed_seconds: float
    generation_config: dict


def hf_token():
    """Reuse environment, Colab secret, or HF's existing cached login; never print it."""
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    if token:
        return token
    try:
        from google.colab import userdata
        token = userdata.get("HF_TOKEN")
        if token:
            return token
    except ImportError:
        pass
    except Exception as exc:
        # Missing or inaccessible Colab secrets can fall back to the cached login.
        if type(exc).__name__ not in ("SecretNotFoundError", "NotebookAccessError"):
            raise
    from huggingface_hub import get_token
    return get_token()


class HFBackend:
    def __init__(self, config: dict):
        os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
        import torch
        from huggingface_hub import HfApi
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

        if not torch.cuda.is_available():
            raise RuntimeError("Select a GPU runtime in Colab (Runtime > Change runtime type), then rerun.")
        if config["quantization"] not in ("nf4", "none"):
            raise ValueError("quantization must be nf4 or none")
        token = hf_token()
        # Pin the resolved commit for tokenizer AND weights, even when requested revision is main.
        revision = HfApi().model_info(config["model_id"], revision=config["model_revision"], token=token).sha
        if not revision:
            raise RuntimeError("Could not resolve immutable model revision")
        dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
        self.tokenizer = AutoTokenizer.from_pretrained(config["model_id"], revision=revision, token=token, trust_remote_code=False)
        template = self.tokenizer.get_chat_template()
        if "enable_thinking" not in template:
            raise ValueError("This v0 backend requires a template with an explicit enable_thinking switch. Validate a new backend before changing model families.")
        kwargs = dict(revision=revision, token=token, trust_remote_code=False,
                      device_map={"": 0}, dtype=dtype, attn_implementation="sdpa")
        if config["quantization"] == "nf4":
            kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=dtype)
        self.model = AutoModelForCausalLM.from_pretrained(config["model_id"], **kwargs).eval()
        self.torch = torch
        self.context_limit = min(config["context_limit"], self.model.config.max_position_embeddings)
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.benchmark = False
        # Some GPU kernels remain nondeterministic; metadata explicitly records this limitation.
        torch.use_deterministic_algorithms(True, warn_only=True)
        versions = {}
        for package in ("torch", "transformers", "accelerate", "bitsandbytes", "huggingface-hub", "numpy", "pandas", "matplotlib"):
            try:
                versions[package] = importlib.metadata.version(package)
            except importlib.metadata.PackageNotFoundError:
                versions[package] = None
        self.metadata = {
            "model_id": config["model_id"], "model_revision": revision,
            "requested_model_revision": config["model_revision"], "backend": "transformers",
            "quantization": config["quantization"], "compute_dtype": str(dtype),
            "enable_thinking": False, "context_limit": self.context_limit,
            "generation_policy": "explicit-settings-no-model-defaults-v1",
            "chat_template_hash": digest(template), "gpu": torch.cuda.get_device_name(0),
            "gpu_memory_gib": round(torch.cuda.get_device_properties(0).total_memory / 2**30, 2),
            "cuda_version": torch.version.cuda, "python": platform.python_version(),
            "versions": versions, "determinism": "per-call seed; deterministic algorithms warn-only; cross-hardware bitwise equivalence not guaranteed",
        }

    def generate(self, messages: list[dict], seed: int, generation_config: dict) -> Generation:
        from transformers import GenerationConfig, set_seed

        rendered = self.tokenizer.apply_chat_template(messages, tokenize=False,
                                                      add_generation_prompt=True, enable_thinking=False)
        encoded = self.tokenizer(rendered, return_tensors="pt", add_special_tokens=False)
        count = encoded["input_ids"].shape[-1]
        if count + generation_config["max_new_tokens"] > self.context_limit:
            raise ValueError("Prompt exceeds frozen context budget; no silent truncation is allowed")
        encoded = {key: value.to(self.model.device) for key, value in encoded.items()}
        set_seed(seed)
        # Construct from scratch so inherited checkpoint generation defaults cannot drift.
        eos = self.model.generation_config.eos_token_id
        if eos is None:
            eos = self.tokenizer.eos_token_id
        if eos is None:
            raise ValueError("Model/tokenizer has no end-of-sequence token")
        eos_ids = eos if isinstance(eos, list) else [eos]
        pad = self.tokenizer.pad_token_id
        gc = GenerationConfig(**generation_config, eos_token_id=eos,
                              pad_token_id=pad if pad is not None else eos_ids[0], use_cache=True)
        # Transformers >=4.50 can replace explicitly supplied global-default values
        # (including do_sample=False) with checkpoint defaults. Disable that merge,
        # resolve token fallbacks, and save the effective config rather than the request.
        gc, _ = self.model._prepare_generation_config(gc, use_model_defaults=False)
        for key, value in generation_config.items():
            if getattr(gc, key) != value:
                raise RuntimeError(f"Generation setting changed before inference: {key}")
        started = time.monotonic()
        with self.torch.inference_mode():
            output = self.model.generate(**encoded, generation_config=gc, use_model_defaults=False)
        continuation = output[0, count:]
        self.torch.cuda.synchronize()
        return Generation(
            raw_text=self.tokenizer.decode(continuation, skip_special_tokens=True),
            rendered_prompt=rendered, input_tokens=count, output_tokens=len(continuation),
            truncated=len(continuation) >= gc.max_new_tokens and int(continuation[-1]) not in eos_ids,
            elapsed_seconds=time.monotonic() - started, generation_config=gc.to_dict(),
        )
