import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

AI_KEYWORDS = (
    "AI_", "MODEL", "SCRIBE", "ESM", "SEPSIS", "PREDICTIVE", "ALGORITHM",
    "THIRD_PARTY", "CLOUD_EGRESS", "AMBIENT", "LLM", "COPILOT", "ABRIDGE", "DAX"
)

HTI1_REQUIRED_FIELDS = (
    "intervention_name",
    "developer_organization",
    "intended_use",
    "patient_population_training",
    "local_validation_completed",
    "human_override_mechanism",
    "patient_disclosure_provided",
)

def load_audit_events(path: Path) -> list[dict]:
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else data.get("events", [])
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def audit_ehr_timeline(events: list[dict]) -> dict:
    sorted_events = sorted(events, key=lambda r: r.get("timestamp", ""))
    ai_triggers = []
    unconsented_ai = []
    unreviewed_scribe_signs = []
    draft_timestamps = {}

    for idx, ev in enumerate(sorted_events, start=1):
        ts = ev.get("timestamp", "UNKNOWN_TS")
        actor = f"{ev.get('user_id', '')} {ev.get('role', '')}".strip()
        action = ev.get("action", "").strip()
        resource = ev.get("resource", "").strip()
        consent = str(ev.get("patient_consent_verified", "")).strip().upper()
        combined = f"{actor} {action} {resource}".upper()

        is_ai = any(k in combined for k in AI_KEYWORDS)
        if is_ai:
            entry = {
                "seq": idx,
                "timestamp": ts,
                "actor": actor,
                "action": action,
                "resource": resource,
                "consent_verified": consent == "TRUE",
            }
            ai_triggers.append(entry)
            if consent != "TRUE":
                unconsented_ai.append(entry)
            if "DRAFT" in action.upper() or "SCRIBE" in combined:
                draft_timestamps[resource] = ts

        if "SIGN" in action.upper() and ("NO_EDIT" in action.upper() or "0_EDITS" in combined):
            unreviewed_scribe_signs.append({
                "seq": idx,
                "timestamp": ts,
                "actor": actor,
                "resource": resource,
                "prior_ai_draft_ts": draft_timestamps.get(resource, "NONE_RECORDED"),
            })

    canonical_bytes = json.dumps(sorted_events, sort_keys=True).encode("utf-8")
    evidence_sha256 = hashlib.sha256(canonical_bytes).hexdigest()

    return {
        "total_audit_records": len(sorted_events),
        "ai_system_events_detected": len(ai_triggers),
        "unconsented_ai_events_count": len(unconsented_ai),
        "rubber_stamped_ai_notes_count": len(unreviewed_scribe_signs),
        "evidence_bundle_sha256": evidence_sha256,
        "unconsented_ai_events": unconsented_ai,
        "rubber_stamped_ai_notes": unreviewed_scribe_signs,
    }

def audit_hti1_manifest(path: Path | None) -> dict:
    if path is None or not path.exists():
        return {
            "manifest_provided": False,
            "status": "DEFICIENT_NO_ONC_HTI1_DISCLOSURE_PRODUCED",
            "missing_attributes": list(HTI1_REQUIRED_FIELDS),
        }
    manifest = json.loads(path.read_text(encoding="utf-8"))
    models = manifest if isinstance(manifest, list) else manifest.get("interventions", [])
    deficiencies = []
    for m in models:
        missing = [f for f in HTI1_REQUIRED_FIELDS if not str(m.get(f, "")).strip()]
        unvalidated = str(m.get("local_validation_completed", "")).upper() != "TRUE"
        undisclosed = str(m.get("patient_disclosure_provided", "")).upper() != "TRUE"
        if missing or unvalidated or undisclosed:
            deficiencies.append({
                "intervention_name": m.get("intervention_name", "UNNAMED_MODEL"),
                "missing_fields": missing,
                "unvalidated_locally": unvalidated,
                "undisclosed_to_patient": undisclosed,
            })
    return {
        "manifest_provided": True,
        "interventions_audited": len(models),
        "deficiencies_found": len(deficiencies),
        "details": deficiencies,
    }

def main():
    parser = argparse.ArgumentParser(description="Oikonomia EHR & ONC HTI-1 AI Forensic Verifier")
    parser.add_argument("--audit", required=True, help="Path to ASTM E2147 EHR audit log (.csv or .json)")
    parser.add_argument("--hti1", required=False, help="Optional path to ONC HTI-1 DSI disclosure JSON")
    parser.add_argument("--out", default="forensic_ai_audit_report.json", help="Output forensic JSON report")
    args = parser.parse_args()

    events = load_audit_events(Path(args.audit))
    ehr_report = audit_ehr_timeline(events)
    hti1_report = audit_hti1_manifest(Path(args.hti1) if args.hti1 else None)

    final_report = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "tool": "Oikonomia EHR & ONC HTI-1 Clinical AI Forensic Verifier v1.0",
        "author": "Joseph Iko (Oikonomia Hardware Architecture Lab)",
        "ehr_audit_findings": ehr_report,
        "onc_hti1_compliance": hti1_report,
    }
    Path(args.out).write_text(json.dumps(final_report, indent=2), encoding="utf-8")
    print(json.dumps(final_report, indent=2))

if __name__ == "__main__":
    main()