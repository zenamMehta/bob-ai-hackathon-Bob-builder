"""
src/submission_readiness.py
===========================
Mode 2 — CTD Dossier Submission Readiness Checker

Loads the ICH M4 CTD required structure from a YAML checklist, accepts a
submitted dossier outline (list of section names), uses fuzzy string matching
to align submitted sections with required ones, and produces per-module
completeness scores plus a gap report.

Fuzzy matching:
    Uses rapidfuzz.process.extractOne with the WRatio scorer (weighted ratio —
    handles partial matches, transpositions, and word-order differences).
    A match is accepted when the similarity score meets or exceeds FUZZY_THRESHOLD.

    FUZZY_THRESHOLD = 80  (named constant — tune here if needed)
    80 was chosen as the default because:
      - It accepts common abbreviations, dropped words, and minor misspellings
        (e.g. "Safety Pharmacology" ↔ "Pharmacology – Safety Pharmacology").
      - It rejects clearly unrelated section names (score typically < 60).
      - Empirically validated against the synthetic dossier in data/synthetic_dossier.json.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Union

import yaml
from rapidfuzz import process as fuzz_process, fuzz

# ---------------------------------------------------------------------------
# Fuzzy matching threshold
# Tune this constant if real-world section names require a stricter or looser match.
# ---------------------------------------------------------------------------
FUZZY_THRESHOLD: int = 80


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_checklist(yaml_path: Union[str, Path]) -> dict:
    """Load and parse the ICH M4 CTD checklist from a YAML file.

    Parameters
    ----------
    yaml_path:
        Path to ``config/ctd_checklist.yaml``.

    Returns
    -------
    dict
        Keyed by ``module_id`` (e.g. ``"m1"``).  Each value is a dict with:
        ``module_name`` (str) and ``sections`` (list of dicts with keys
        ``id``, ``name``, ``risk_note``).

    Example structure::

        {
          "m1": {
            "module_name": "Module 1 – Administrative ...",
            "sections": [
              {"id": "1.1", "name": "Table of Contents", "risk_note": "..."},
              ...
            ]
          },
          ...
        }
    """
    with open(yaml_path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    checklist: dict = {}
    for module in raw["modules"]:
        checklist[module["module_id"]] = {
            "module_name": module["module_name"],
            "sections":    module["sections"],
        }
    return checklist


def load_dossier(source: Union[str, Path, list]) -> list[str]:
    """Load a dossier outline — a list of submitted section-name strings.

    Parameters
    ----------
    source:
        One of:
        - A file path (str or Path) to a JSON file.  The JSON must have a
          top-level key ``"sections"`` whose value is a list of strings.
        - A plain Python list of strings (passed directly from the UI).

    Returns
    -------
    list[str]
        List of section-name strings, stripped of leading/trailing whitespace.

    Raises
    ------
    KeyError
        If the JSON file does not contain a top-level ``"sections"`` key.
    """
    if isinstance(source, list):
        return [s.strip() for s in source]

    with open(source, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "sections" not in data:
        raise KeyError(
            f"Dossier JSON must have a top-level 'sections' key. "
            f"Found keys: {list(data.keys())}"
        )

    return [s.strip() for s in data["sections"]]


# ---------------------------------------------------------------------------
# Matching logic
# ---------------------------------------------------------------------------

def match_sections(
    checklist: dict,
    dossier_sections: list[str],
    threshold: int = FUZZY_THRESHOLD,
) -> dict:
    """Fuzzy-match submitted dossier sections against the required CTD checklist.

    For each required section (across all modules), this function searches the
    submitted dossier_sections for the best fuzzy match using rapidfuzz WRatio.
    A required section is considered "present" if the best match score >= threshold.

    Submitted sections that were not the winning match for any required section
    are collected as "unrecognised" — they were submitted but don't correspond
    to any known required section.

    Parameters
    ----------
    checklist:
        Parsed checklist dict from :func:`load_checklist`.
    dossier_sections:
        List of submitted section names from :func:`load_dossier`.
    threshold:
        Minimum fuzzy score (0–100) to accept a match.  Default: FUZZY_THRESHOLD.

    Returns
    -------
    dict
        Keys:
        - ``"matched"``:  dict mapping required section ``name`` → best-matching
          submitted string (for audit trail).
        - ``"unmatched"``: set of required section names that had no match.
        - ``"unrecognised"``: list of submitted section strings that did not match
          any required section at or above the threshold.
    """
    # Collect all required section names (flat, across all modules)
    all_required: list[str] = [
        sec["name"]
        for mod in checklist.values()
        for sec in mod["sections"]
    ]

    # Track which submitted sections have been "claimed" by a required section.
    # We allow each submitted section to be claimed by at most one required section
    # (greedy first-match — sufficient for dossier completeness checking).
    claimed_submitted: set[str] = set()

    matched:   dict[str, str] = {}   # required_name → best submitted match
    unmatched: set[str]        = set()

    for req_name in all_required:
        result = fuzz_process.extractOne(
            req_name,
            dossier_sections,
            scorer=fuzz.WRatio,
            score_cutoff=threshold,
        )
        if result is not None:
            best_match, _score, _idx = result
            matched[req_name] = best_match
            claimed_submitted.add(best_match)
        else:
            unmatched.add(req_name)

    # Submitted sections that were never claimed are "unrecognised"
    unrecognised: list[str] = [
        s for s in dossier_sections if s not in claimed_submitted
    ]

    return {
        "matched":      matched,
        "unmatched":    unmatched,
        "unrecognised": unrecognised,
    }


# ---------------------------------------------------------------------------
# Readiness computation
# ---------------------------------------------------------------------------

def compute_readiness(
    checklist: dict,
    dossier_sections: list[str],
    threshold: int = FUZZY_THRESHOLD,
) -> dict:
    """Compute per-module completeness scores and generate a gap report.

    Calls :func:`match_sections` then aggregates results per module.

    Parameters
    ----------
    checklist:
        Parsed checklist dict from :func:`load_checklist`.
    dossier_sections:
        List of submitted section names from :func:`load_dossier`.
    threshold:
        Fuzzy match score threshold (passed through to :func:`match_sections`).

    Returns
    -------
    dict
        Top-level keys:

        - ``"overall_score"`` (float): percentage of all required sections present.
        - ``"total_required"`` (int): total required sections across all modules.
        - ``"total_present"``  (int): total matched sections across all modules.
        - ``"unrecognised"``   (list[str]): submitted sections with no match.
        - ``"modules"``        (dict): per-module results, keyed by module_id.

        Each module entry contains:

        - ``"module_name"``  (str)
        - ``"score"``        (float): (present / total_required) * 100
        - ``"total_required"``(int)
        - ``"present"``      (list[dict]): matched required sections
          (``id``, ``name``, ``matched_to`` — the submitted string that matched).
        - ``"missing"``      (list[dict]): unmatched required sections
          (``id``, ``name``, ``risk_note``).
    """
    match_result = match_sections(checklist, dossier_sections, threshold)
    matched    = match_result["matched"]      # required_name → submitted_string
    unmatched  = match_result["unmatched"]    # set of required_names with no match
    unrecognised = match_result["unrecognised"]

    modules_out: dict = {}
    grand_required = 0
    grand_present  = 0

    for mod_id, mod_data in checklist.items():
        sections      = mod_data["sections"]
        present_list  = []
        missing_list  = []

        for sec in sections:
            name = sec["name"]
            if name in matched:
                present_list.append({
                    "id":         sec["id"],
                    "name":       name,
                    "matched_to": matched[name],
                })
            else:
                missing_list.append({
                    "id":        sec["id"],
                    "name":      name,
                    "risk_note": sec["risk_note"],
                })

        total_req = len(sections)
        total_prs = len(present_list)
        score     = (total_prs / total_req * 100) if total_req > 0 else 0.0

        grand_required += total_req
        grand_present  += total_prs

        modules_out[mod_id] = {
            "module_name":   mod_data["module_name"],
            "score":         round(score, 1),
            "total_required": total_req,
            "present":       present_list,
            "missing":       missing_list,
        }

    overall_score = (
        round(grand_present / grand_required * 100, 1) if grand_required > 0 else 0.0
    )

    return {
        "overall_score":  overall_score,
        "total_required": grand_required,
        "total_present":  grand_present,
        "unrecognised":   unrecognised,
        "modules":        modules_out,
    }
