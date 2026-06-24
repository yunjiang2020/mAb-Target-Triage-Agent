import re
import json
from google.cloud import storage

BUCKET = "project-two-dats-5750-adc-kb"
BLOB = "adc_kb.json" 

def norm(value) -> str:
    """normalize keys to uppercase, alphanumeric only ('Her-2' == 'HER2')."""
    return "".join(ch for ch in str(value).upper() if ch.isalnum())


def aliases(target_cell) -> list[str]:
    """B7-H3 / CD276 -> [B7H3,CD276]"""
    parts = []
    for chunk in str(target_cell).split("/"):
        parts.extend(re.findall(r"\(([^)]*)\)", chunk))   # parenthetical synonyms
        parts.append(re.sub(r"\([^)]*\)", "", chunk))      # base name w/o ()
    return [k for k in (norm(p) for p in parts) if k]

def load_index() -> dict:
    client = storage.Client()
    raw = client.bucket(BUCKET).blob(BLOB).download_as_text()
    index = {}
    for program in json.loads(raw):
        for alias in aliases(program.get("target")):
            index.setdefault(alias, []).append(program)
    return index


def get_curated_adc_knowledge(antigen_name: str) -> dict | None:
    """Search curated ADC program precedent for the target antigen.

    Returns ADC programs regarding the target plus failure reason and mechanism
    Absence from the KB means no curated ADC precedent for this target.

    Args:
        antigen_name: Target antigen (e.g. "HER2")

    Returns:
        dict with target, summary counts, and programs (list)
        None if the target has no curated precedent in the KB.
    """
    global index
    index = load_index()

    programs = index.get(norm(antigen_name))
    if not programs:
        return None

    return {
        "target": antigen_name,
        "n_programs": len(programs),
        "n_approved": sum("approved" in str(p["status"]).lower() for p in programs),
        "n_failed": sum(bool(p["fail_reason"]) for p in programs),
        "programs": programs,
        "n_notes": sum(bool(p["notes"]) for p in programs),
    
    }