<<<<<<< HEAD
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
=======
# 🚀 Drug Safety Signal Detector &
Regulatory Submission Readiness
Checker

> ⚠️ **Replace everything in `[ ]` brackets with your actual content before submission.**

---

## 👥 Team

| Field | Value |
|---|---|
| **Team Name** | Bobs builder |
| **Track** | Pharma & Biotech |
| **Team Lead** | Manan Manojkumar Patel — 25me073@charusat.edu.in |
| **Members** | Zenam Rasheshbhai Mehta, Keval Desai, Aum Umang Pathak |

---

## 🎯 Problem Statement

> In 2–3 sentences: What problem does your project solve? Who experiences this problem?

Pharmacovigilance teams must monitor 20M+ adverse event reports in FAERS to catch dangerous drug safety signals before they cause harm, Vioxx caused 27,000+ heart attacks before its signal was formally acted on. Regulatory affairs teams face a parallel problem: a CTD dossier spans 100,000+ pages across five modules, and a single missing or incorrectly named section triggers a rejection costing 6-12 months and $50-100M. Both teams face the same root cause: too much complex, high-stakes data for manual review to catch reliably.
---

## 💡 Solution

> In 2–3 sentences: What did you build? How does it solve the problem above?

A single Streamlit application with two modes, built using IBM Bob. Signal Detection computes the Proportional Reporting Ratio and chi-squared statistic for every drug-event pair in an adverse event dataset, flagging signals against standard pharmacovigilance thresholds, including correct handling of drug-exclusive reactions as infinite-PRR signals while guarding against single-report flukes. Submission Readiness compares a CTD dossier outline against the ICH M4 required structure using fuzzy string matching, scoring completeness per module and generating a gap report with regulator-facing risk notes.

---

## ✨ Key Features

- **Feature 1:** Statistical signal detection: PRR and chi-squared calculation per drug-event pair, following the Evans (2001) pharmacovigilance method
- **Feature 2:** Infinite-PRR handling with a fluke guard: drug-exclusive reactions are treated as the strongest signal type, but still require a minimum case count before being flagged
- **Feature 3:** ICH M4 fuzzy-matched readiness checking: dossier sections are matched against the required CTD structure even when naming varies, with per-module completeness scoring
- **Feature 4:** Regulator-facing gap reports: every missing section comes with a plain-English risk note explaining why it matters
- **Feature 5:** Fully offline, rule-based summaries: both modes generate plain-English narrative summaries with zero external API calls, and accept file upload or bundled synthetic data

---

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| **Languages** | [e.g., Python, TypeScript] |
| **Frameworks** | [e.g., FastAPI, React] |
| **IBM Technologies** | [e.g., watsonx.ai, IBM Bob, IBM Cloud] |
| **Databases** | [e.g., PostgreSQL, Redis] |
| **Other** | [e.g., Docker, GitHub Actions] |

---

## 📁 Repository Structure

```
├── src/                  # All source code
├── docs/                 # Written documentation
│   ├── problem-statement.md
│   ├── solution-overview.md
│   ├── architecture.md
│   └── setup-guide.md
├── demo/                 # Demo artifacts
│   ├── screenshots/      # App screenshots
│   └── demo-video-link.txt  # Link to demo video
├── presentation/         # Slide deck
└── submission.yaml       # Structured submission metadata
>>>>>>> 9bbe15357d6621b4b66ecd56ee9388f266cc6783
```

---

<<<<<<< HEAD
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
=======
## ⚡ How to Run

> **Copy these exact steps from your [`docs/setup-guide.md`](docs/setup-guide.md)**

```bash
# 1. Clone the repo
git clone https://github.com/[your-repo].git
cd [your-repo]

# 2. Install dependencies
[your install command here]

# 3. Configure environment
cp .env.example .env
# Edit .env with your values

# 4. Run the project
[your run command here]
```

---

## 🖥️ Demo

| Artifact | Link |
|---|---|
| 📹 Demo Video | [See demo/demo-video-link.txt](demo/demo-video-link.txt) |
| 🌐 Live Demo | [See demo/live-demo-url.txt](demo/live-demo-url.txt) |
| 🖼️ Screenshots | [See demo/screenshots/](demo/screenshots/) |
| 📊 Presentation | [See presentation/slides.pdf](presentation/) |

---

## ⚠️ Known Limitations

> Be honest — judges appreciate transparency over overclaiming.

- [Limitation 1: e.g., "Authentication is mocked — not production-ready"]
- [Limitation 2: e.g., "Only tested on Chrome"]
- [Limitation 3: e.g., "Feature X is scaffolded but not fully implemented"]

---

## 🏅 What We're Most Proud Of

[Tell the judges what part of your submission is strongest and worth paying close attention to.]

---
>>>>>>> 9bbe15357d6621b4b66ecd56ee9388f266cc6783
