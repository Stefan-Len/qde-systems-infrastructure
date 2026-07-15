from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class QDECandidateSide(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"


class QDEEvaluationStatus(str, Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    BLOCKED = "blocked"


class QDEReasonCode(str, Enum):
    CANDIDATE_ACCEPTED = "qde_candidate_accepted"
    PROVENANCE_MISSING = "qde_provenance_missing"
    NO_LOOKAHEAD_GUARD_FAILED = "qde_no_lookahead_guard_failed"
    MATERIAL_VALIDATION_MISSING = "qde_material_validation_missing"
    PUBLIC_GATE_SCORE_FAILED = "qde_public_gate_score_failed"


@dataclass(frozen=True)
class QDESyntheticResearchInput:
    run_id: str
    system: str
    validation_profile: str
    instrument_focus: str
    generated_at_utc: str

    def validate(self) -> None:
        required = {
            "run_id": self.run_id,
            "system": self.system,
            "validation_profile": self.validation_profile,
            "instrument_focus": self.instrument_focus,
            "generated_at_utc": self.generated_at_utc,
        }
        for field, value in required.items():
            if not value.strip():
                raise ValueError(f"{field} is required")


@dataclass(frozen=True)
class QDEValidationCandidate:
    candidate_id: str
    family_id: str
    side: QDECandidateSide
    decision_ts_event: str
    public_gate_score: Decimal
    deterministic_order_key: str
    source_feature_refs: tuple[str, ...]
    reference_level_refs: tuple[str, ...]
    session_context: str
    cross_market_context: str
    no_lookahead_confirmed: bool
    material_validation: bool

    def validate(self) -> None:
        required = {
            "candidate_id": self.candidate_id,
            "family_id": self.family_id,
            "decision_ts_event": self.decision_ts_event,
            "deterministic_order_key": self.deterministic_order_key,
            "session_context": self.session_context,
            "cross_market_context": self.cross_market_context,
        }
        for field, value in required.items():
            if not value.strip():
                raise ValueError(f"{field} is required")
        if self.public_gate_score <= Decimal("0"):
            raise ValueError("public_gate_score must be positive")


@dataclass(frozen=True)
class QDEValidationDecision:
    candidate_id: str
    family_id: str
    side: QDECandidateSide
    status: QDEEvaluationStatus
    reason_code: QDEReasonCode
    public_gate_score: Decimal

    def public_payload(self) -> dict[str, str]:
        return {
            "candidate_id": self.candidate_id,
            "family_id": self.family_id,
            "side": self.side.value,
            "status": self.status.value,
            "reason_code": self.reason_code.value,
            "public_gate_score": str(self.public_gate_score),
        }


@dataclass(frozen=True)
class QDEExecutionBoundarySummary:
    risk_gate_status: str
    execution_boundary_mode: str
    accepted_candidate_count: int
    broker_execution_included: bool

    def public_payload(self) -> dict[str, object]:
        return {
            "risk_gate_status": self.risk_gate_status,
            "execution_boundary_mode": self.execution_boundary_mode,
            "accepted_candidate_count": self.accepted_candidate_count,
            "broker_execution_included": self.broker_execution_included,
        }


@dataclass(frozen=True)
class QDEPublicValidationResult:
    run_id: str
    system: str
    validation_profile: str
    instrument_focus: str
    decisions: tuple[QDEValidationDecision, ...]
    scorecard: "QDEPortfolioSummary"
    execution_boundary: QDEExecutionBoundarySummary
    audit_event_count: int
    result_id: str
    deterministic_output: bool

    def public_summary(self) -> dict[str, object]:
        return {
            "run_id": self.run_id,
            "system": self.system,
            "validation_profile": self.validation_profile,
            "instrument_focus": self.instrument_focus,
            "candidate_count": self.scorecard.candidate_count,
            "accepted_count": self.scorecard.accepted_count,
            "rejected_count": self.scorecard.rejected_count,
            "blocked_count": self.scorecard.blocked_count,
            "risk_gate_status": self.execution_boundary.risk_gate_status,
            "execution_boundary": self.execution_boundary.execution_boundary_mode,
            "broker_execution_included": self.execution_boundary.broker_execution_included,
            "audit_event_count": self.audit_event_count,
            "deterministic_output": self.deterministic_output,
            "result_id": self.result_id,
        }
