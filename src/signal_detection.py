"""
src/signal_detection.py
=======================
Mode 1 — Adverse Event Signal Detection

Implements the Proportional Reporting Ratio (PRR) and chi-squared disproportionality
analysis on a table of adverse event reports.

Reference:
    Evans S.J.W., Waller P.C., Davis S. (2001) "Use of proportional reporting ratios
    (PRRs) for signal generation from spontaneous adverse drug reaction reports."
    Pharmacoepidemiology and Drug Safety, 10(6): 483–486.

Pharmacovigilance thresholds applied (Evans 2001 / EMA guidance):
    PRR   >= 2   : the drug reports this event at least twice as often as the background rate
    cases >= 3   : minimum evidence base; single/double reports may be coincidental
    chi2  >= 4   : ~p < 0.05 on 1 degree of freedom; statistical significance filter

    Special case — PRR = Inf:
    When (c + d) == 0 the reaction has never been reported for any *other* drug.
    This "event exclusivity" is the strongest possible disproportionality signal.
    Chi-squared is undefined in this case (the 2×2 table is degenerate), so the
    chi-squared threshold is waived.  The case-count guard (>= 3) is still applied
    to exclude single-report flukes.
"""

from __future__ import annotations

import math
from typing import Union

import pandas as pd
from scipy.stats import chi2_contingency

# ---------------------------------------------------------------------------
# Required columns in the input adverse-event DataFrame
# ---------------------------------------------------------------------------
REQUIRED_COLUMNS: list[str] = [
    "report_id",
    "drug_name",
    "reaction",
]

# ---------------------------------------------------------------------------
# Flagging thresholds  (Evans 2001 / EMA guidance)
# ---------------------------------------------------------------------------
PRR_THRESHOLD = 2.0      # signal if PRR >= this value
CASE_THRESHOLD = 3       # signal if case count (a) >= this value
CHI2_THRESHOLD = 4.0     # signal if chi-squared >= this value (finite-PRR pairs only)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_faers(source: Union[str, pd.DataFrame]) -> pd.DataFrame:
    """Load and validate an adverse-event report table.

    Parameters
    ----------
    source:
        Either a file path (str) to a CSV file or an already-loaded DataFrame.

    Returns
    -------
    pd.DataFrame
        Cleaned DataFrame with at least the required columns present.
        ``drug_name`` and ``reaction`` are lower-cased and stripped of whitespace
        to ensure consistent grouping.

    Raises
    ------
    ValueError
        If any required column is missing from the data.
    """
    if isinstance(source, pd.DataFrame):
        df = source.copy()
    else:
        df = pd.read_csv(source)

    # Validate required columns
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f"Input data is missing required column(s): {missing}. "
            f"Expected columns: {REQUIRED_COLUMNS}"
        )

    # Normalise string fields used for grouping
    df["drug_name"] = df["drug_name"].astype(str).str.strip().str.lower()
    df["reaction"]  = df["reaction"].astype(str).str.strip().str.lower()

    return df


def compute_signals(df: pd.DataFrame) -> pd.DataFrame:
    """Compute PRR and chi-squared statistics for every drug-event pair.

    For each unique (drug_name, reaction) pair the function builds the standard
    2×2 pharmacovigilance contingency table:

        ┌──────────────────────────────┬──────────────────────────────┐
        │  a: this event, this drug   │  b: other events, this drug  │
        ├──────────────────────────────┼──────────────────────────────┤
        │  c: this event, other drugs  │  d: other events, other drugs│
        └──────────────────────────────┴──────────────────────────────┘

    PRR  = (a / (a + b)) / (c / (c + d))
    chi2 = computed by scipy.stats.chi2_contingency on [[a, b], [c, d]]

    Parameters
    ----------
    df:
        Cleaned DataFrame returned by :func:`load_faers`.

    Returns
    -------
    pd.DataFrame
        One row per drug-event pair with columns:
        ``drug``, ``event``, ``case_count``, ``prr``, ``chi_squared``, ``flagged``.

        ``prr`` is typed as *object* (mixed str/float) so the sentinel string
        ``"Inf"`` coexists with numeric values without dtype coercion.
        ``chi_squared`` is ``float``; NaN for Inf-PRR pairs.
        ``flagged`` is ``bool``.

        Rows are sorted: Inf-PRR flagged rows first, then finite-PRR rows by
        PRR descending.
    """
    # ── Step 1: count reports per (drug, event) pair  ─────────────────────
    # a[drug][event] = number of reports of `event` for `drug`
    pair_counts: pd.Series = (
        df.groupby(["drug_name", "reaction"]).size().rename("a")
    )

    # ── Step 2: marginal counts  ───────────────────────────────────────────
    # drug_totals[drug]     = total reports for this drug  (a + b)
    # event_totals[event]   = total reports of this event  (a + c)
    drug_totals:  pd.Series = df.groupby("drug_name").size()
    event_totals: pd.Series = df.groupby("reaction").size()
    N: int = len(df)   # grand total of all reports

    # ── Step 3: build results row by row  ─────────────────────────────────
    rows: list[dict] = []

    for (drug, event), a in pair_counts.items():
        ab = int(drug_totals[drug])    # a + b  (all reports for this drug)
        ac = int(event_totals[event])  # a + c  (all reports of this event)

        b = ab - a          # other events for this drug
        c = ac - a          # this event for other drugs
        d = N - ab - c      # other events for other drugs  (= N - ab - ac + a)

        # ── PRR calculation ─────────────────────────────────────────────
        # Numerator: proportion of this drug's reports that mention this event
        numerator_denom = ab  # (a + b); always >= 1 because a >= 1

        if c == 0:
            # Event exclusivity: c == 0 means this reaction was never reported
            # for any other drug in the database.
            #
            # Two sub-cases:
            #   (c + d) == 0  → no other drug has any reports at all (degenerate)
            #   (c + d) >  0  → other drugs exist but none reported this reaction
            # In both cases the PRR denominator (c / (c+d)) is 0, making PRR
            # undefined / infinite.
            #
            # We represent this as "Inf" — the strongest possible signal.
            # Chi-squared is also undefined for a zero-row, so we set it to NaN
            # and waive the chi2 threshold for flagging.
            prr_value    = "Inf"
            chi2_value   = float("nan")
            # Flag if case count meets the minimum evidence threshold
            # (chi-squared threshold is waived — exclusivity is sufficient)
            flagged = a >= CASE_THRESHOLD

        else:
            # ── Standard finite-PRR case ────────────────────────────────
            # PRR = (a / ab) / (c / (c + d))
            # c > 0 here, so (c / (c + d)) > 0 — division is safe.
            prr_value = (a / ab) / (c / (c + d))

            # Chi-squared on the 2×2 contingency table
            # correction=False: Yates' correction is NOT applied; Evans (2001)
            # uses the uncorrected statistic.
            try:
                chi2_value = chi2_contingency(
                    [[a, b], [c, d]], correction=False
                )[0]  # index 0 is the test statistic
            except ValueError:
                # scipy raises ValueError if any expected frequency is 0;
                # fall back gracefully.
                chi2_value = float("nan")

            # Apply the three-threshold Evans (2001) flagging rule:
            #   PRR >= 2    — at least twice the background rate
            #   cases >= 3  — minimum evidence base
            #   chi2 >= 4   — statistically significant at ~p < 0.05
            flagged = (
                prr_value  >= PRR_THRESHOLD  and
                a          >= CASE_THRESHOLD and
                (not math.isnan(chi2_value) and chi2_value >= CHI2_THRESHOLD)
            )

        rows.append({
            "drug":        drug,
            "event":       event,
            "case_count":  int(a),
            "prr":         prr_value,
            "chi_squared": chi2_value,
            "flagged":     flagged,
        })

    # ── Step 4: sort — Inf rows first, then finite PRR descending ─────────
    result = pd.DataFrame(rows)

    # Separate Inf-PRR rows from finite-PRR rows for clean sorting
    inf_mask    = result["prr"] == "Inf"
    inf_rows    = result[inf_mask].copy()
    finite_rows = result[~inf_mask].copy()

    # Convert prr to float for sorting within finite rows
    finite_rows["_prr_sort"] = finite_rows["prr"].astype(float)
    finite_rows = finite_rows.sort_values("_prr_sort", ascending=False).drop(
        columns=["_prr_sort"]
    )

    # Sort Inf rows by case_count descending (more evidence = more important)
    inf_rows = inf_rows.sort_values("case_count", ascending=False)

    result = pd.concat([inf_rows, finite_rows], ignore_index=True)

    # Ensure consistent column order
    result = result[["drug", "event", "case_count", "prr", "chi_squared", "flagged"]]

    return result
