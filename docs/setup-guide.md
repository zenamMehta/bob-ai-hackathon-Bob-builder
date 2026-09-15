# Setup Guide

## Prerequisites

- Python **3.10 or higher**
- `pip` (comes with Python)
- No API keys, databases, or environment variables required

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/zenamMehta/bob-ai-hackathon-Bob-builder.git
cd bob-ai-hackathon-Bob-builder

# 2. (Optional) Create a virtual environment
python -m venv .venv
source .venv/bin/activate      # macOS / Linux
# .venv\Scripts\activate       # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

## Running the Application

```bash
streamlit run src/app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

Both tabs (**Signal Detection** and **Submission Readiness**) work immediately
using the bundled synthetic data — no file upload is needed to explore the demo.

## Using Your Own Data

**Mode 1 — Signal Detection:**  
Upload a CSV with at least these columns: `report_id`, `drug_name`, `reaction`.  
Optional columns: `patient_age`, `patient_sex`, `report_date`, `outcome_severity`.

**Mode 2 — Submission Readiness:**  
Upload a JSON file with a top-level `"sections"` key containing a list of
section-name strings:

```json
{
  "sections": [
    "Table of Contents",
    "Investigator's Brochure",
    "Safety Pharmacology"
  ]
}
```

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| `streamlit` | 1.35.0 | Web UI framework |
| `pandas` | 2.2.2 | Data loading and tabular processing |
| `scipy` | 1.13.1 | Chi-squared statistic (`chi2_contingency`) |
| `rapidfuzz` | 3.9.3 | Fuzzy string matching for dossier sections |
| `pyyaml` | 6.0.2 | Parsing `config/ctd_checklist.yaml` |

## Troubleshooting

| Issue | Solution |
|---|---|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` again, or activate your virtual environment. |
| App doesn't open in browser | Navigate to `http://localhost:8501` manually. |
| `ValueError: Input data is missing required column(s)` | Check that your CSV has `report_id`, `drug_name`, and `reaction` columns. |
| `KeyError: 'sections'` | Your dossier JSON must have a top-level `"sections"` key. |
