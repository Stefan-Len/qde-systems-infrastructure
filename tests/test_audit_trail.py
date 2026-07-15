from dataclasses import replace

from qde_systems_infrastructure import QDEAuditTrail, verify_qde_audit_trail


def test_qde_audit_trail_verifies_clean_events() -> None:
    audit = QDEAuditTrail()
    audit.append("qde_public_validation_started", {"run_id": "qde-systems-test"})
    audit.append("qde_public_validation_completed", {"result": "accepted"})

    assert verify_qde_audit_trail(audit.events) is True


def test_qde_audit_trail_detects_payload_tampering() -> None:
    audit = QDEAuditTrail()
    first = audit.append("qde_public_validation_started", {"run_id": "qde-systems-test"})
    second = audit.append("qde_public_validation_completed", {"result": "accepted"})
    tampered = replace(second, payload={"result": "rewritten"})

    assert verify_qde_audit_trail((first, tampered)) is False
