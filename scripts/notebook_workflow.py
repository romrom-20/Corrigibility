"""Notebook approval/resume helpers. No model loading or inference.

Kept outside the hashed experiment package so workflow-only changes do not
invalidate an otherwise matching, human-approved experiment snapshot.
"""
from pathlib import Path

from corrigibility_bench.runner import approve_smoke, read_json, validate_review


def ensure_smoke_approval(smoke_run, review_file=None):
    """Record an explicit review once, or validate and reuse the saved approval.

    An explicit review must equal the saved human fields; never overwrite a
    signed approval or silently ignore a different/rejected supplied review.
    Returns the approval path. Validation errors retain their concrete cause.
    """
    smoke_run = Path(smoke_run)
    approval_path = smoke_run / "review_approval.json"
    manifest = read_json(smoke_run / "manifest.json")
    review_path = Path(review_file) if review_file and str(review_file).strip() else None
    if approval_path.exists():
        saved = read_json(approval_path)
        validate_review(smoke_run, saved, manifest["config"], manifest["model"])
        if review_path is not None:
            supplied = read_json(review_path)
            validate_review(smoke_run, supplied, manifest["config"], manifest["model"])
            human_fields = lambda value: {k: v for k, v in value.items() if k != "approved_at"}
            if human_fields(supplied) != human_fields(saved):
                raise ValueError("Supplied review differs from saved approval; preserve both and resolve the discrepancy. No approval was overwritten.")
        return approval_path
    if review_path is None:
        raise ValueError(f"No saved approval at {approval_path}. Set REVIEW_FILE to the completed human review; a reviewer name alone does not approve scaling.")
    supplied = read_json(review_path)
    if (supplied.get("approve_pilot") is not True or
            supplied.get("task_comprehension_acceptable") is not True):
        raise ValueError(
            f"Review decision for {smoke_run.name}: "
            f"reviewer={supplied.get('reviewer')!r}, "
            f"task_comprehension_acceptable={supplied.get('task_comprehension_acceptable')!r}, "
            f"approve_pilot={supplied.get('approve_pilot')!r}. "
            "Signed review is not pilot approval unless both decisions are true. "
            "Preserve the human decision; ask about an ambiguous sign-off instead of changing flags.")
    approve_smoke(smoke_run, review_path)
    return approval_path
