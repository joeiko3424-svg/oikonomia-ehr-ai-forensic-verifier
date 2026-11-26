# Oikonomia EHR & ONC HTI-1 Clinical AI Forensic Verifier

Open-source forensic parser built for patients, bereaved families, and medical malpractice counsel to audit ASTM E2147 Electronic Health Record (EHR) metadata trails and ONC HTI-1 (45 C.F.R. 170.315(b)(11)) predictive Decision Support Intervention (DSI) disclosures.

## Quickstart

    python oik_ehr_forensic.py --audit sample_astm_e2147_audit.csv --out forensic_report.json

## From Post-Incident Forensics to Hardware-Enforced Prevention (`OIK-DFIS-V2-MED`)
While `oik_ehr_forensic.py` audits `ASTM E2147` metadata trails and `ONC HTI-1` disclosures *after* an adverse clinical event, healthcare systems, EHR vendors, and clinical AI developers can prevent unconsented cloud API egress and post-incident log tampering at the physical bus layer using **OIK-DFIS-V2-MED** (bare-metal PCIe BAR0 hardware consent latch and tamper-proof 256-bit rolling flight recorder, benchmarked at **84.51 ns** posted write latency and **6–9 W** steady-state core power).

## Zero-Integration 72-Hour Clinical AI & Forensic Audit Sprint
Hospital compliance teams, clinical trial sponsors, and legal audit teams do not need to provision FPGA hardware or install custom drivers:

1. **Submit De-Identified / Synthetic Logs:** Email de-identified `ASTM E2147` audit CSV/JSON exports or simulated clinical AI API call traces to `contact@oikonomia-platform.com`.
2. **Air-Gapped Vault Execution:** Automated `ONC HTI-1` timeline verification and bare-metal PCIe BAR0 containment validation execute inside Oikonomia's single-tenant, zero-egress hardware vault.
3. **Cryptographically Signed Audit Dossier:** Receive a `SHA-256` signed forensic and hardware containment dossier within 72 hours (`$7,500–$12,000` flat sprint via AWS Marketplace Private Offer or invoice).
