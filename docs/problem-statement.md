# Problem Statement

## Background

The pharmaceutical industry faces two distinct but structurally similar
high-stakes data-review problems that currently rely heavily on manual effort.

**FDA FAERS (pharmacovigilance):** The FDA Adverse Event Reporting System
contains over 20 million individual case safety reports accumulated since 1969,
growing by hundreds of thousands of new reports each year. These reports are
the primary early-warning system for post-market drug safety — dangerous signals
hidden in this data can cause patient harm if they go undetected.

**CTD dossier review (regulatory submissions):** A Common Technical Document
dossier for a new drug application spans five modules and up to 100,000+ pages.
Regulatory agencies (FDA, EMA, PMDA) require a precisely structured submission;
a single missing or incorrectly named section causes outright rejection.

---

## The Problem

**Pharmacovigilance signal detection** is performed by trained safety scientists
who must manually scan large volumes of adverse event data to identify drug-event
combinations that appear disproportionately often compared to the rest of the
database. The standard statistical method — the Proportional Reporting Ratio
(PRR) with chi-squared confirmation — is well-established but computationally
tedious to apply at scale without tooling. A delayed signal detection contributed
to Vioxx remaining on the market long enough to cause an estimated 27,000+
cardiovascular events, many fatal.

**CTD submission completeness checking** is performed by regulatory affairs
professionals who must cross-check every submitted section title against the
ICH M4 required structure, taking into account minor naming variations and
abbreviations across regions and sponsors. A single gap causes a Complete
Response Letter (rejection), triggering a resubmission cycle of 6–12 months
and costs estimated at $50–100M in delayed market entry.

---

## Who is Affected

- **Pharmacovigilance scientists** at pharmaceutical companies, CROs, and
  regulatory agencies who monitor post-market safety signals.
- **Regulatory affairs professionals** preparing and reviewing NDA/MAA
  submissions for new drug applications.

Both roles involve repeated, high-cognitive-load document review work that is
amenable to algorithmic assistance.

---

## Why It Matters

- Drug safety signals detected late cause preventable patient harm and
  regulatory action (market withdrawal, label changes, black-box warnings).
- Failed CTD submissions cost $50–100M in delayed revenue per cycle and delay
  patient access to beneficial therapies.
- Both problems involve well-defined standards (Evans 2001 PRR thresholds;
  ICH M4 CTD structure) that can be encoded and automated.

---

## Why Existing Solutions Fall Short

Commercial pharmacovigilance platforms (e.g., Argus Safety, Oracle AERS) exist
but are expensive enterprise systems inaccessible to smaller sponsors, CROs, and
academic researchers. No lightweight, open, explainable PRR tool exists that
handles the PRR = Inf edge case correctly.

CTD completeness tools are typically proprietary regulatory management systems.
No open tool performs fuzzy-matched completeness checking against the ICH M4
structure, which is necessary because submitted section names are rarely an
exact string match to the standard.
