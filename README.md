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
```

---

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
