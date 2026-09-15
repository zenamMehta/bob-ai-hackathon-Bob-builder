# Drug Safety Signal Detector & Regulatory Submission Readiness Checker

A Streamlit application built for the IBM BoB AI Innovation Hackathon 2026,
addressing the **Pharma & Biotech** problem statement.

---

## 👥 Team

| Field | Value |
|---|---|
| **Team Name** | Bobs Builder |
| **Track** | Pharma & Biotech |
| **Team Lead** | Manan Manojkumar Patel — 25me073@charusat.edu.in |
| **Members** | Zenam Rasheshbhai Mehta, Keval Desai, Aum Umang Pathak |

---

## 🎯 Problem Statement

Pharmacovigilance teams must monitor 20M+ adverse event reports in FAERS to catch dangerous drug safety signals before they cause harm — Vioxx caused 27,000+ heart attacks before its signal was formally acted on. Regulatory affairs teams face a parallel problem: a CTD dossier spans 100,000+ pages across five modules, and a single missing or incorrectly named section triggers a rejection costing 6–12 months and $50–100M. Both teams face the same root cause: too much complex, high-stakes data for manual review to catch reliably.

---

## 💡 Solution

A single Streamlit application with two modes, built using IBM Bob. **Signal Detection** computes the Proportional Reporting Ratio (PRR) and chi-squared statistic for every drug-event pair in an adverse event dataset, flagging signals against standard pharmacovigilance thresholds — including correct handling of drug-exclusive reactions as infinite-PRR signals while guarding against single-report flukes. **Submission Readiness** compares a CTD dossier outline against the ICH M4 required structure using fuzzy string matching, scoring completeness per module and generating a gap report with regulator-facing risk notes.

---

## ✨ Key Features

- **Statistical signal detection:** PRR and chi-squared calculation per drug-event pair, following the Evans (2001) pharmacovigilance method.
- **Infinite-PRR handling with a fluke guard:** drug-exclusive reactions are treated as the strongest signal type, but still require a minimum case count before being flagged.
- **ICH M4 fuzzy-matched readiness checking:** dossier sections are matched against the required CTD structure even when naming varies, with per-module completeness scoring.
- **Regulator-facing gap reports:** every missing section comes with a plain-English risk note explaining why it matters.
- **Fully offline, rule-based summaries:** both modes generate plain-English narrative summaries with zero external API calls, and accept file upload or bundled synthetic data.

---

## 📁 Repository Structure

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
│   ├── problem-statement.md
│   ├── solution-overview.md
│   ├── architecture.md          # Architecture narrative + Mermaid data-flow diagram
│   └── setup-guide.md
├── requirements.txt
└── README.md
```

---

## ⚡ How to Run

```bash
# 1. Clone the repo
git clone https://github.com/zenamMehta/bob-ai-hackathon-Bob-builder.git
cd bob-ai-hackathon-Bob-builder

# 2. Install dependencies (Python 3.10+ required)
pip install -r requirements.txt

# 3. Run the app
streamlit run src/app.py
```

The app opens in your browser. Both tabs work immediately with the bundled synthetic data — no file upload or environment variables required.

---

## 🖥️ Demo

| Artifact | Link |
|---|---|
| 🖼️ Screenshots | [See demo/screenshots/](demo/screenshots/) |
| 📁 Live Demo URL | [See demo/live-demo-url.txt](demo/live-demo-url.txt) |

---

## 📊 Thresholds

| Threshold | Value | Source |
|---|---|---|
| PRR signal threshold | ≥ 2 | Evans et al. (2001) |
| Minimum case count | ≥ 3 | EMA guidance |
| Chi-squared threshold | ≥ 4 | Evans et al. (2001) |
| Fuzzy match score | ≥ 80 | `FUZZY_THRESHOLD` in `submission_readiness.py` |

---

## ⚠️ Known Limitations

- No authentication — this is a local prototype, not production-ready.
- The row-by-row loop in `compute_signals` is clear and correct at demo scale but will be slow on full FAERS (millions of rows); a vectorised pandas implementation would be needed for production.
- Fuzzy matching is greedy (first-match), which can occasionally mis-assign sections when two required names are very similar.

---

## 🏅 What We're Most Proud Of

The rigorous, standards-faithful implementation of the Evans (2001) PRR algorithm — including the principled handling of the PRR = Inf edge case (event exclusivity), the chi-squared waiver for degenerate tables, and the three-threshold flagging logic. The result is pharmacovigilance signal detection that a real regulatory scientist would recognise as methodologically sound, not just a demonstration.
