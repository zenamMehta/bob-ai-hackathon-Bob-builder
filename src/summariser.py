"""
src/summariser.py
=================
Rule-based natural language summary generators for both application modes.

All summaries are derived entirely from computed results — no external API calls,
no ML models.  The functions produce plain-English paragraphs suitable for
display in Streamlit ``st.info`` boxes.
"""

from __future__ import annotations

import math

import pandas as pd


# ---------------------------------------------------------------------------
# Mode 1 — Signal Detection summary
# ---------------------------------------------------------------------------

def summarise_signals(results_df: pd.DataFrame) -> str:
    """Generate a plain-English summary of the PRR signal detection results.

    Parameters
    ----------
    results_df:
        DataFrame returned by ``signal_detection.compute_signals()``.
        Expected columns: ``drug``, ``event``, ``case_count``, ``prr``,
        ``chi_squared``, ``flagged``.

    Returns
    -------
    str
        A one-to-three sentence summary suitable for ``st.info()``.
    """
    if results_df.empty:
        return (
            "No drug-event pairs were found in the data. "
            "Please check that the uploaded file contains valid adverse event records."
        )

    total_pairs   = len(results_df)
    flagged_df    = results_df[results_df["flagged"] == True]
    flagged_count = len(flagged_df)
    inf_flagged   = flagged_df[flagged_df["prr"] == "Inf"]

    # ── No signals detected ───────────────────────────────────────────────
    if flagged_count == 0:
        return (
            f"Analysis of {total_pairs:,} drug-event pairs identified no signals "
            f"meeting the standard pharmacovigilance thresholds "
            f"(PRR \u2265 2, cases \u2265 3, chi-squared \u2265 4). "
            f"No further regulatory action is indicated by this dataset alone."
        )

    # ── Identify top signal ───────────────────────────────────────────────
    # Inf-PRR rows sort first; otherwise take the row with the highest numeric PRR
    top_row  = flagged_df.iloc[0]
    top_drug = top_row["drug"].title()
    top_evt  = top_row["event"].title()
    top_cases = int(top_row["case_count"])

    if top_row["prr"] == "Inf":
        top_prr_str = "infinite PRR (event reported exclusively for this drug)"
    else:
        top_prr_str = f"PRR\u00a0=\u00a0{float(top_row['prr']):.2f}"
        chi2_val = top_row["chi_squared"]
        if not (isinstance(chi2_val, float) and math.isnan(chi2_val)):
            top_prr_str += f", chi-squared\u00a0=\u00a0{float(chi2_val):.2f}"

    # ── Count exclusive (Inf) signals ─────────────────────────────────────
    inf_note = ""
    if len(inf_flagged) > 0:
        n_inf = len(inf_flagged)
        inf_note = (
            f" Of these, {n_inf} signal{'s' if n_inf > 1 else ''} "
            f"{'have' if n_inf > 1 else 'has'} an infinite PRR — "
            f"{'these reactions were' if n_inf > 1 else 'this reaction was'} reported "
            f"exclusively for one drug, representing the strongest possible signal type."
        )

    # ── Build summary sentence ─────────────────────────────────────────────
    summary = (
        f"Analysis of {total_pairs:,} drug-event pairs identified "
        f"{flagged_count} signal{'s' if flagged_count > 1 else ''} "
        f"meeting the Evans\u00a0(2001) pharmacovigilance thresholds "
        f"(PRR\u00a0\u2265\u00a02, cases\u00a0\u2265\u00a03, chi-squared\u00a0\u2265\u00a04). "
        f"The strongest signal is \u2018{top_drug} \u2192 {top_evt}\u2019 "
        f"with {top_prr_str} based on {top_cases} case{'s' if top_cases != 1 else ''}."
        f"{inf_note}"
    )

    return summary


# ---------------------------------------------------------------------------
# Mode 2 — Submission Readiness summary
# ---------------------------------------------------------------------------

def summarise_readiness(readiness: dict) -> str:
    """Generate a plain-English summary of the CTD dossier readiness results.

    Parameters
    ----------
    readiness:
        Dict returned by ``submission_readiness.compute_readiness()``.
        Expected top-level keys: ``overall_score``, ``total_required``,
        ``total_present``, ``unrecognised``, ``modules``.

    Returns
    -------
    str
        A two-to-four sentence summary suitable for ``st.info()``.
    """
    overall   = readiness["overall_score"]
    total_req = readiness["total_required"]
    total_prs = readiness["total_present"]
    gap_count = total_req - total_prs
    modules   = readiness["modules"]
    unrec     = readiness.get("unrecognised", [])

    # ── Identify best and worst modules ───────────────────────────────────
    module_scores = [
        (mod_id, data["module_name"], data["score"], len(data["missing"]))
        for mod_id, data in modules.items()
    ]
    best  = max(module_scores, key=lambda x: x[2])
    worst = min(module_scores, key=lambda x: x[2])

    # ── Overall verdict ───────────────────────────────────────────────────
    if overall == 100.0:
        verdict = "The dossier appears complete"
    elif overall >= 85.0:
        verdict = "The dossier is substantially complete"
    elif overall >= 60.0:
        verdict = "The dossier has notable gaps"
    else:
        verdict = "The dossier has significant completeness issues"

    # ── Best module phrase ─────────────────────────────────────────────────
    best_name  = best[1].split("\u2013")[-1].strip()   # strip "Module N – " prefix
    worst_name = worst[1].split("\u2013")[-1].strip()

    if best[2] == 100.0:
        best_phrase = f"{best_name} is fully complete"
    else:
        best_phrase = f"{best_name} has the highest score ({best[2]:.0f}%)"

    # ── Worst module phrase ────────────────────────────────────────────────
    worst_gaps = worst[3]
    if worst_gaps == 0:
        worst_phrase = f"all modules meet the required structure"
    else:
        # Surface the first missing section from the worst module as an example
        worst_missing = modules[worst[0]]["missing"]
        example_gap   = worst_missing[0]["name"] if worst_missing else None
        worst_phrase = (
            f"{worst_name} has the most gaps ({worst_gaps} missing section"
            f"{'s' if worst_gaps > 1 else ''})"
        )
        if example_gap:
            worst_phrase += f", including \u2018{example_gap}\u2019"

    # ── Unrecognised sections note ─────────────────────────────────────────
    unrec_note = ""
    if unrec:
        n_unrec = len(unrec)
        unrec_note = (
            f" Additionally, {n_unrec} submitted section"
            f"{'s were' if n_unrec > 1 else ' was'} not matched to any required "
            f"ICH\u00a0M4 section and {'are' if n_unrec > 1 else 'is'} listed as "
            f"unrecognised — these may be supplementary documents or incorrectly titled sections."
        )

    summary = (
        f"{verdict} with an overall completeness score of {overall:.0f}% "
        f"({total_prs} of {total_req} required sections present). "
        f"{best_phrase.capitalize()}, while {worst_phrase}. "
        f"A total of {gap_count} gap{'s' if gap_count != 1 else ''} "
        f"{'were' if gap_count != 1 else 'was'} identified — each is listed below "
        f"with its regulatory risk note."
        f"{unrec_note}"
    )

    return summary
