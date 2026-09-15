# Solution Overview

## What We Built

A single Streamlit web application with two independent modes, each addressing
one of the two problems described in the problem statement. The app runs entirely
locally with no internet connection required, no API keys, and no database — it
uses only Python scientific libraries and bundled synthetic data.

---

## How It Works

### Mode 1 — Signal Detection

1. The user uploads a CSV of adverse event reports (or uses the bundled
   synthetic FAERS dataset of 200 rows).
2. `signal_detection.load_faers` validates and normalises the input, checking
   for the required columns (`report_id`, `drug_name`, `reaction`).
3. `signal_detection.compute_signals` iterates over every unique
   `(drug_name, reaction)` pair and builds the standard 2×2 pharmacovigilance
   contingency table, computing the Proportional Reporting Ratio (PRR) and
   chi-squared statistic (via `scipy.stats.chi2_contingency`).
4. Each pair is flagged as a signal if all three Evans (2001) thresholds are
   met: PRR ≥ 2, case count ≥ 3, chi-squared ≥ 4. Pairs where the reaction
   was never reported for any other drug receive PRR = Inf (the chi-squared
   threshold is waived; the case-count guard is retained).
5. Results are displayed as a ranked table (Inf-PRR rows first, then finite PRR
   descending), summary metrics, and a plain-English narrative summary.
6. Users can download the full results as a CSV.

### Mode 2 — Submission Readiness

1. The user uploads a JSON dossier outline (or uses the bundled synthetic CTD
   dossier covering ~74% of required sections).
2. `submission_readiness.load_checklist` parses `config/ctd_checklist.yaml`
   — the ICH M4 CTD required structure encoded as 5 modules and 57 sections,
   each annotated with a regulatory risk note.
3. `submission_readiness.match_sections` uses `rapidfuzz.process.extractOne`
   with the WRatio scorer to fuzzy-match each submitted section name against
   all required section names. A match is accepted at similarity score ≥ 80.
4. `submission_readiness.compute_readiness` aggregates results per module:
   per-module completeness score, list of present sections (with matched
   submitted name for audit), and list of missing sections with risk notes.
   Submitted sections that did not match any required section are collected as
   "unrecognised."
5. The UI displays overall completeness, a per-module breakdown with expanders,
   an unrecognised-sections list, and a plain-English narrative summary.

---

## Architecture Diagram

See [`architecture.md`](architecture.md) for the detailed Mermaid data-flow
diagram. The high-level structure is:

```
[User] → [Streamlit UI: app.py]
              ↓                    ↓
  [signal_detection.py]   [submission_readiness.py]
              ↓                    ↓
        [summariser.py]     [summariser.py]
              ↓                    ↓
       [st.info summary]   [st.info summary]
```

---

## Key Design Decisions

| Decision | Rationale |
|---|---|
| Rule-based summaries, no LLM | Zero latency, no API cost, no hallucination risk — the structured output of each mode already contains all the grounding needed for a faithful summary. |
| PRR = Inf sentinel string, not float("inf") | Avoids dtype coercion issues in mixed-type pandas columns; makes downstream display logic explicit and testable. |
| rapidfuzz WRatio scorer | Handles partial matches, transpositions, and word-order variation — all common in real dossier section names — better than simple ratio alone. |
| FUZZY_THRESHOLD = 80 as a named constant | Empirically validated against the synthetic dossier; easily adjustable in one place without hunting through code. |
| Separation of UI and logic | `signal_detection.py`, `submission_readiness.py`, and `summariser.py` have no Streamlit imports — they can be unit-tested independently and reused outside the app. |

---

## IBM Technologies Used

- **IBM Bob:** Used to develop the full application — from scaffolding the
  project structure and implementing the PRR algorithm to writing the fuzzy
  matching logic and generating the synthetic datasets. Bob's code generation
  and iterative refinement capabilities accelerated development significantly.
