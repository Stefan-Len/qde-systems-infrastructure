# deterministic-execution-infrastructure
# Copyright (c) 2026 Stefan Len
# SPDX-License-Identifier: MIT
from dataclasses import replace

from execution_infrastructure import AuditLedger, verify_audit_chain


def test_audit_chain_verifies_clean_events() -> None:
    ledger = AuditLedger()
    ledger.append("cycle_started", {"run_id": "run-1"})
    ledger.append("risk_evaluated", {"allowed": True})

    assert verify_audit_chain(ledger.events) is True


def test_audit_chain_detects_tampered_payload() -> None:
    ledger = AuditLedger()
    first = ledger.append("cycle_started", {"run_id": "run-1"})
    second = ledger.append("risk_evaluated", {"allowed": True})
    tampered = replace(second, payload={"allowed": False})

    assert verify_audit_chain((first, tampered)) is False


def test_audit_chain_detects_reordered_events() -> None:
    ledger = AuditLedger()
    first = ledger.append("cycle_started", {"run_id": "run-1"})
    second = ledger.append("risk_evaluated", {"allowed": True})

    assert verify_audit_chain((second, first)) is False


def test_audit_chain_detects_missing_middle_event() -> None:
    ledger = AuditLedger()
    first = ledger.append("cycle_started", {"run_id": "run-1"})
    ledger.append("risk_evaluated", {"allowed": True})
    third = ledger.append("execution_planned", {"signal_id": "sig-1"})

    assert verify_audit_chain((first, third)) is False


def test_audit_chain_detects_previous_hash_rewrite() -> None:
    ledger = AuditLedger()
    first = ledger.append("cycle_started", {"run_id": "run-1"})
    second = ledger.append("risk_evaluated", {"allowed": True})
    rewritten = replace(second, previous_hash=first.event_hash[::-1])

    assert verify_audit_chain((first, rewritten)) is False
