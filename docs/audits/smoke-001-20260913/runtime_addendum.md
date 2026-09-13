# Runtime finding after the initial transcript review

The live Colab runtime was subsequently accessible. Its smoke completion digest verifies, and the saved source hashes match the source used in Colab. The loaded model is Qwen/Qwen3-8B revision `b968826d9c46dd6066d109eabc6255188de91218`, NF4 on an NVIDIA A100 40 GB, with Transformers 4.57.6.

A substantive decoding bug was found. In this installed version, `_prepare_generation_config` may replace global-default-valued settings in an explicitly supplied `GenerationConfig` with checkpoint defaults unless `use_model_defaults=False` is passed. In particular, the intended smoke `do_sample=False` can become `True`, with temperature 0.6 and top-p 0.95. The library emitted this warning during the smoke run. The old backend recorded the pre-resolution config, so it did not reliably record the effective decoding settings.

The transcript annotations still describe the supplied outputs. Treat that run as a preserved run with a decoding-protocol deviation, not verified greedy smoke. No comparison should pool it with the corrected run or claim its original generation metadata was accurate. The fix disables checkpoint-default merging, verifies each requested setting before inference, and records the resolved config. A new smoke experiment ID and source snapshot are required; no original raw output or approval is changed.

The transferred review remains AI-authored and does not constitute human smoke approval. A live no-inference regression check reconstructs the old config resolution and checks corrected smoke and pilot settings for all three call types. Its output is saved separately with the new source snapshot.
