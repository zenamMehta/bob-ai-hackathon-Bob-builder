"""
src/app.py
==========
Streamlit entry point — Drug Safety Signal Detector & Regulatory Submission
Readiness Checker.

Run from the project root:
    streamlit run src/app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Make sure the project root is on sys.path so sibling src/ modules resolve.
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent.parent.resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.signal_detection import load_faers, compute_signals          # noqa: E402
from src.submission_readiness import (                                  # noqa: E402
    load_checklist,
    load_dossier,
    compute_readiness,
)
from src.summariser import summarise_signals, summarise_readiness      # noqa: E402

# ---------------------------------------------------------------------------
# Paths to bundled synthetic data and config
# ---------------------------------------------------------------------------
SYNTHETIC_FAERS    = ROOT / "data"   / "synthetic_faers.csv"
SYNTHETIC_DOSSIER  = ROOT / "data"   / "synthetic_dossier.json"
CTD_CHECKLIST_YAML = ROOT / "config" / "ctd_checklist.yaml"


# ===========================================================================
# Page config
# ===========================================================================
st.set_page_config(
    page_title="Drug Safety Signal Detector",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("💊 Drug Safety Tools")
    st.markdown("**IBM BoB AI Innovation Hackathon 2026**")
    st.markdown("*Pharma & Biotech track*")
    st.divider()
    st.markdown(
        "### Mode 1 — Signal Detection\n"
        "Ingests adverse event reports and computes the **Proportional Reporting "
        "Ratio (PRR)** and chi-squared statistic for every drug-event pair. "
        "Flags signals using the Evans (2001) pharmacovigilance thresholds: "
        "PRR ≥ 2, cases ≥ 3, chi-squared ≥ 4.  Events reported exclusively for "
        "one drug are assigned PRR = Inf and flagged automatically if cases ≥ 3."
    )
    st.divider()
    st.markdown(
        "### Mode 2 — Submission Readiness\n"
        "Checks a CTD dossier outline against the **ICH M4 required structure** "
        "using fuzzy string matching (threshold 80).  Reports per-module "
        "completeness scores, a gap list with regulatory risk notes, and any "
        "sections submitted but not recognised in the standard."
    )
    st.divider()
    st.caption("Synthetic demo data is used when no file is uploaded.")


# ===========================================================================
# Main title
# ===========================================================================
st.title("Drug Safety Signal Detector & Regulatory Submission Readiness Checker")

# ===========================================================================
# Tabs
# ===========================================================================
tab1, tab2 = st.tabs(["🔬 Mode 1 — Signal Detection", "📋 Mode 2 — Submission Readiness"])


# ===========================================================================
# TAB 1 — Signal Detection
# ===========================================================================
with tab1:
    st.header("Signal Detection", divider="blue")
    st.markdown(
        "Upload a CSV of adverse event reports, or run the analysis on the "
        "bundled synthetic FAERS dataset. The app computes the **PRR** and "
        "**chi-squared** statistic for every drug-event pair and highlights "
        "flagged signals."
    )

    # ── File upload ──────────────────────────────────────────────────────
    uploaded_faers = st.file_uploader(
        "Upload adverse event CSV (optional)",
        type=["csv"],
        help=(
            "Required columns: report_id, drug_name, reaction. "
            "Optional: patient_age, patient_sex, report_date, outcome_severity."
        ),
        key="faers_upload",
    )

    using_synthetic_faers = uploaded_faers is None
    if using_synthetic_faers:
        st.info(
            "ℹ️  No file uploaded — using the bundled synthetic FAERS dataset "
            f"(`{SYNTHETIC_FAERS.name}`).  Upload a CSV above to analyse your own data.",
            icon=None,
        )

    # ── Run button ───────────────────────────────────────────────────────
    run_signals = st.button("▶  Run Signal Detection", type="primary", key="run_signals")

    if run_signals:
        with st.spinner("Computing PRR and chi-squared statistics…"):
            try:
                source = uploaded_faers if not using_synthetic_faers else SYNTHETIC_FAERS
                df_raw = load_faers(source)
                results = compute_signals(df_raw)
            except Exception as exc:
                st.error(f"Error loading or processing data: {exc}")
                st.stop()

        # ── Summary metrics ───────────────────────────────────────────
        total_pairs    = len(results)
        flagged_count  = int(results["flagged"].sum())
        inf_count      = int((results["prr"] == "Inf").sum())

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total reports",      f"{len(df_raw):,}")
        col2.metric("Drug-event pairs",   f"{total_pairs:,}")
        col3.metric("⚑ Flagged signals",  flagged_count,
                    delta="requires review" if flagged_count else None,
                    delta_color="inverse" if flagged_count else "off")
        col4.metric("∞ PRR = Inf signals", inf_count)

        st.divider()

        # ── Results table ─────────────────────────────────────────────
        st.subheader("Ranked Drug-Event Pairs")
        st.caption(
            "Sorted by signal strength: PRR = Inf rows first, then finite PRR descending. "
            "🔴 Flagged rows meet all pharmacovigilance thresholds."
        )

        # Build a display copy with formatted numerics
        display_df = results.copy()
        display_df["drug"]   = display_df["drug"].str.title()
        display_df["event"]  = display_df["event"].str.title()

        # Format chi_squared: NaN → "—", floats to 2 d.p.
        def _fmt_chi2(v):
            try:
                import math
                if math.isnan(float(v)):
                    return "—"
                return f"{float(v):.2f}"
            except (TypeError, ValueError):
                return "—"

        display_df["chi_squared"] = display_df["chi_squared"].apply(_fmt_chi2)

        # Format PRR: keep "Inf" as-is, floats to 2 d.p.
        def _fmt_prr(v):
            if v == "Inf":
                return "Inf ∞"
            try:
                return f"{float(v):.2f}"
            except (TypeError, ValueError):
                return str(v)

        display_df["prr"] = display_df["prr"].apply(_fmt_prr)
        display_df["flagged"] = display_df["flagged"].map({True: "🔴 Yes", False: "No"})

        display_df = display_df.rename(columns={
            "drug":        "Drug",
            "event":       "Adverse Event",
            "case_count":  "Cases (a)",
            "prr":         "PRR",
            "chi_squared": "Chi-squared",
            "flagged":     "Signal Flagged",
        })

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Cases (a)":     st.column_config.NumberColumn(format="%d"),
                "Signal Flagged": st.column_config.TextColumn(width="small"),
            },
        )

        # ── NL Summary ────────────────────────────────────────────────
        st.divider()
        st.subheader("Plain-English Summary")
        summary_text = summarise_signals(results)
        st.info(summary_text)

        # ── Flagged-only table ────────────────────────────────────────
        flagged_rows = results[results["flagged"] == True]
        if not flagged_rows.empty:
            st.divider()
            st.subheader("⚑ Flagged Signals Detail")
            st.caption("Only pairs that meet all three pharmacovigilance thresholds.")

            flagged_display = flagged_rows.copy()
            flagged_display["drug"]  = flagged_display["drug"].str.title()
            flagged_display["event"] = flagged_display["event"].str.title()
            flagged_display["prr"]   = flagged_display["prr"].apply(_fmt_prr)
            flagged_display["chi_squared"] = flagged_display["chi_squared"].apply(_fmt_chi2)
            flagged_display = flagged_display.drop(columns=["flagged"])
            flagged_display = flagged_display.rename(columns={
                "drug":        "Drug",
                "event":       "Adverse Event",
                "case_count":  "Cases (a)",
                "prr":         "PRR",
                "chi_squared": "Chi-squared",
            })
            st.dataframe(flagged_display, use_container_width=True, hide_index=True)

        # ── Download ──────────────────────────────────────────────────
        st.divider()
        csv_bytes = display_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇  Download full results as CSV",
            data=csv_bytes,
            file_name="signal_detection_results.csv",
            mime="text/csv",
        )


# ===========================================================================
# TAB 2 — Submission Readiness
# ===========================================================================
with tab2:
    st.header("Submission Readiness", divider="green")
    st.markdown(
        "Upload a JSON dossier outline, or check the bundled synthetic CTD "
        "dossier against the **ICH M4 required structure**.  The app uses fuzzy "
        "string matching to map submitted sections to required ones and reports "
        "completeness scores and gaps per module."
    )

    # ── Load checklist (always from disk) ────────────────────────────────
    try:
        checklist = load_checklist(CTD_CHECKLIST_YAML)
    except Exception as exc:
        st.error(f"Failed to load CTD checklist YAML: {exc}")
        st.stop()

    # ── File upload ───────────────────────────────────────────────────────
    uploaded_dossier = st.file_uploader(
        "Upload dossier outline JSON (optional)",
        type=["json"],
        help='JSON must have a top-level "sections" key containing a list of section-name strings.',
        key="dossier_upload",
    )

    using_synthetic_dossier = uploaded_dossier is None
    if using_synthetic_dossier:
        st.info(
            "ℹ️  No file uploaded — using the bundled synthetic dossier "
            f"(`{SYNTHETIC_DOSSIER.name}`).  Upload a JSON above to check your own dossier.",
            icon=None,
        )

    # ── Run button ────────────────────────────────────────────────────────
    run_readiness = st.button("▶  Check Submission Readiness", type="primary", key="run_readiness")

    if run_readiness:
        with st.spinner("Matching sections and computing completeness scores…"):
            try:
                source = uploaded_dossier if not using_synthetic_dossier else SYNTHETIC_DOSSIER
                dossier_sections = load_dossier(source)
                readiness = compute_readiness(checklist, dossier_sections)
            except Exception as exc:
                st.error(f"Error loading or processing dossier: {exc}")
                st.stop()

        # ── Overall score metric ──────────────────────────────────────
        overall   = readiness["overall_score"]
        total_req = readiness["total_required"]
        total_prs = readiness["total_present"]
        gap_count = total_req - total_prs
        unrec     = readiness["unrecognised"]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Overall Completeness", f"{overall:.0f}%")
        col2.metric("Sections Present",     f"{total_prs} / {total_req}")
        col3.metric("⚠ Gaps Identified",    gap_count,
                    delta="sections missing" if gap_count else None,
                    delta_color="inverse" if gap_count else "off")
        col4.metric("Unrecognised Sections", len(unrec))

        # Colour the progress bar
        bar_colour = "green" if overall >= 85 else ("orange" if overall >= 60 else "red")
        st.markdown(f"**Overall dossier completeness: {overall:.0f}%**")
        st.progress(int(overall) / 100)

        # ── NL Summary ────────────────────────────────────────────────
        st.divider()
        st.subheader("Plain-English Summary")
        summary_text = summarise_readiness(readiness)
        st.info(summary_text)

        st.divider()
        st.subheader("Per-Module Breakdown")

        # ── Per-module expanders ──────────────────────────────────────
        for mod_id, mod_data in readiness["modules"].items():
            module_name  = mod_data["module_name"]
            score        = mod_data["score"]
            present_list = mod_data["present"]
            missing_list = mod_data["missing"]
            n_req        = mod_data["total_required"]
            n_prs        = len(present_list)

            # Choose icon by score
            if score == 100.0:
                icon = "✅"
            elif score >= 75.0:
                icon = "🟡"
            else:
                icon = "🔴"

            with st.expander(
                f"{icon} {module_name}  —  {score:.0f}%  ({n_prs}/{n_req} sections)",
                expanded=(score < 100.0),
            ):
                st.progress(int(score) / 100)

                if present_list:
                    st.markdown(f"**✔ Present sections ({n_prs})**")
                    for sec in present_list:
                        matched_note = (
                            f' *(matched to: "{sec["matched_to"]}")*'
                            if sec["matched_to"] != sec["name"] else ""
                        )
                        st.markdown(f"- `{sec['id']}` {sec['name']}{matched_note}")

                if missing_list:
                    st.markdown(f"**✗ Missing sections ({len(missing_list)})**")
                    for sec in missing_list:
                        st.markdown(
                            f"- `{sec['id']}` **{sec['name']}**  \n"
                            f"  > ⚠ *{sec['risk_note']}*"
                        )

        # ── Unrecognised sections ─────────────────────────────────────
        if unrec:
            st.divider()
            st.subheader("❓ Unrecognised Sections")
            st.caption(
                "These sections were present in the submitted dossier but could not "
                "be matched to any required ICH M4 section at or above the fuzzy "
                "matching threshold (80).  They may be supplementary documents, "
                "supporting annexes, or incorrectly titled required sections."
            )
            for s in unrec:
                st.markdown(f"- {s}")

        # ── Module score summary table ────────────────────────────────
        st.divider()
        st.subheader("Module Score Summary")
        summary_rows = []
        for mod_id, mod_data in readiness["modules"].items():
            summary_rows.append({
                "Module":    mod_data["module_name"],
                "Score (%)": mod_data["score"],
                "Present":   len(mod_data["present"]),
                "Missing":   len(mod_data["missing"]),
                "Required":  mod_data["total_required"],
            })
        summary_table = pd.DataFrame(summary_rows)
        st.dataframe(
            summary_table,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Score (%)": st.column_config.ProgressColumn(
                    "Score (%)",
                    min_value=0,
                    max_value=100,
                    format="%.0f%%",
                ),
            },
        )
