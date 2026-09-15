# Drug Safety Signal Detector & Regulatory Submission Readiness Checker

A Streamlit application built for the IBM BoB AI Innovation Hackathon 2026,
addressing the **Pharma & Biotech** problem statement.

## Problem

FDA's FAERS database contains 20M+ adverse event reports. Dangerous drug safety
signals can go undetected for too long due to data volume. Separately, CTD drug
approval dossiers span 100,000+ pages, and a single missing section causes
rejection — costing 6–12 months and $50–100M.

This app tackles both problems in one tool.

---

## Modes

### Mode 1 — Signal Detection

Ingests adverse event reports, computes the **Proportional Reporting Ratio
(PRR)** and **chi-squared statistic** for every drug-event pair, and flags
signals using standard pharmacovigilance thresholds:

- PRR ≥ 2, case count ≥ 3, chi-squared ≥ 4 (Evans et al., 2001)
- Events exclusive to a single drug (PRR = Inf) are flagged automatically if
  case count ≥ 3

### Mode 2 — Submission Readiness

Compares a submitted CTD dossier outline against the ICH M4 required structure
using **fuzzy string matching**. Produces per-module completeness scores, a gap
report with plain-English risk notes, and an "unrecognised sections" list.

---

## Layout

```
drug-safety-detector/
├── src/
│   ├── app.py                   # Streamlit entry point
│   ├── signal_detection.py      # PRR + chi-squared core logic (no Streamlit dependency)
│   ├── submission_readiness.py  # CTD fuzzy matching + gap report logic
│   └── summariser.py            # Rule-based NL summary generators
├── data/
│   ├── synthetic_faers.csv      # Synthetic adverse event data (~200 rows)
│   └── synthetic_dossier.json   # Synthetic CTD dossier outline
├── config/
│   └── ctd_checklist.yaml       # ICH M4 CTD required structure (single source of truth)
├── docs/
│   └── architecture.md          # Architecture narrative + Mermaid data-flow diagram
├── requirements.txt
└── README.md
```

---

## Installation

```bash
cd drug-safety-detector
pip install -r requirements.txt
```

Python 3.10+ is required.

---

## Running the App

```bash
streamlit run src/app.py
```

The app opens in your browser. Both tabs work immediately with the bundled
synthetic data — no file upload required.

To use your own data:
- **Mode 1**: upload a CSV with columns `report_id`, `drug_name`, `reaction`,
  `patient_age`, `patient_sex`, `report_date`, `outcome_severity`.
- **Mode 2**: upload a JSON file with a top-level `"sections"` key containing a
  list of section-name strings.

---

## Synthetic Data

`data/synthetic_faers.csv` — 200 synthetic adverse event reports covering 10
drugs and 20 reactions. Deliberate high-PRR signals are embedded to make the
demo illustrative.

`data/synthetic_dossier.json` — a CTD dossier outline covering ~70% of required
ICH M4 sections. Includes intentional misspellings (to exercise fuzzy matching),
genuine gaps across two modules, and a few invented sections (to exercise
unrecognised-section detection).

---

## Thresholds

| Threshold | Value | Source |
|-----------|-------|--------|
| PRR signal threshold | ≥ 2 | Evans et al. (2001) |
| Minimum case count | ≥ 3 | EMA guidance |
| Chi-squared threshold | ≥ 4 | Evans et al. (2001) |
| Fuzzy match score | ≥ 80 | Named constant `FUZZY_THRESHOLD` in `submission_readiness.py` |
