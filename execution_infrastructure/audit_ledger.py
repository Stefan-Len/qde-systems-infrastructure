# qde-systems-infrastructure
# Copyright (c) 2026 Štefan Lengyel, trading as Stefan Len / QDE-Systems
# SPDX-License-Identifier: MIT
"""Append-only audit ledger with SHA-256 hash-chain verification."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class AuditEvent:
    """One immutable audit event."""

    sequence: int
    event_type: str
    payload: dict[str, Any]
    previous_hash: str | None
    event_hash: str


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _event_hash(
    *,
    sequence: int,
    event_type: str,
    payload: dict[str, Any],
    previous_hash: str | None,
) -> str:
    body = {
        "sequence": sequence,
        "event_type": event_type,
        "payload": payload,
        "previous_hash": previous_hash,
    }
    return hashlib.sha256(_stable_json(body).encode("utf-8")).hexdigest()


class AuditLedger:
    """In-memory append-only audit ledger for the showcase runtime."""

    def __init__(self) -> None:
        self._events: list[AuditEvent] = []

    @property
    def events(self) -> tuple[AuditEvent, ...]:
        return tuple(self._events)

    def append(self, event_type: str, payload: dict[str, Any]) -> AuditEvent:
        if not event_type.strip():
            raise ValueError("event_type is required")
        sequence = len(self._events) + 1
        previous_hash = self._events[-1].event_hash if self._events else None
        event_hash = _event_hash(
            sequence=sequence,
            event_type=event_type,
            payload=payload,
            previous_hash=previous_hash,
        )
        event = AuditEvent(
            sequence=sequence,
            event_type=event_type,
            payload=dict(payload),
            previous_hash=previous_hash,
            event_hash=event_hash,
        )
        self._events.append(event)
        return event

    def to_jsonl(self) -> str:
        return "\n".join(_stable_json(asdict(event)) for event in self._events)


def verify_audit_chain(events: tuple[AuditEvent, ...] | list[AuditEvent]) -> bool:
    """Return true when sequence, previous hash, and event hash are consistent."""

    previous_hash: str | None = None
    for expected_sequence, event in enumerate(events, start=1):
        if event.sequence != expected_sequence:
            return False
        if event.previous_hash != previous_hash:
            return False
        expected_hash = _event_hash(
            sequence=event.sequence,
            event_type=event.event_type,
            payload=event.payload,
            previous_hash=event.previous_hash,
        )
        if event.event_hash != expected_hash:
            return False
        previous_hash = event.event_hash
    return True
