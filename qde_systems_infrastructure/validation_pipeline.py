from __future__ import annotations

import hashlib
import json
from decimal import Decimal

from .audit_trail import QDEAuditTrail
from .models import (
    QDEExecutionBoundarySummary,
    QDEEvaluationStatus,
    QDEPublicValidationResult,
    QDEReasonCode,
    QDESyntheticResearchInput,
    QDEValidationCandidate,
    QDEValidationDecision,
)
from .portfolio_scorecard import QDEPortfolioSummary


PUBLIC_PLACEHOLDER_MINIMUM_GATE_SCORE = Decimal("0.70")


class QDEPublicValidationPipeline:
    def __init__(self, *, minimum_public_gate_score: Decimal = PUBLIC_PLACEHOLDER_MINIMUM_GATE_SCORE) -> None:
        if minimum_public_gate_score <= Decimal("0"):
            raise ValueError("minimum_public_gate_score must be positive")
        self.minimum_public_gate_score = minimum_public_gate_score

    def run(
        self,
        *,
        research_input: QDESyntheticResearchInput,
        candidates: tuple[QDEValidationCandidate, ...] | list[QDEValidationCandidate],
    ) -> QDEPublicValidationResult:
        research_input.validate()
        audit = QDEAuditTrail()
        audit.append(
            "qde_public_validation_started",
            {
                "run_id": research_input.run_id,
                "system": research_input.system,
                "validation_profile": research_input.validation_profile,
                "instrument_focus": research_input.instrument_focus,
            },
        )

        ordered_candidates = tuple(
            sorted(candidates, key=lambda item: (item.deterministic_order_key, item.candidate_id))
        )
        decisions: list[QDEValidationDecision] = []
        for candidate in ordered_candidates:
            candidate.validate()
            decision = self._evaluate_candidate(candidate)
            decisions.append(decision)
            audit.append("qde_candidate_evaluated", decision.public_payload())

        decision_tuple = tuple(decisions)
        scorecard = QDEPortfolioSummary.from_decisions(decision_tuple)
        audit.append("qde_portfolio_summary_built", scorecard.public_payload())
        execution_boundary = QDEExecutionBoundarySummary(
            risk_gate_status="qde_public_risk_gate_passed_for_accepted_candidates",
            execution_boundary_mode="review_only_no_broker_adapter",
            accepted_candidate_count=scorecard.accepted_count,
            broker_execution_included=False,
        )
        audit.append(
            "qde_risk_gate_summary_built",
            {
                "risk_gate_status": execution_boundary.risk_gate_status,
                "accepted_candidate_count": execution_boundary.accepted_candidate_count,
            },
        )
        audit.append("qde_execution_boundary_marked", execution_boundary.public_payload())
        result_id = _result_id(
            run_id=research_input.run_id,
            decisions=decision_tuple,
            scorecard=scorecard,
            execution_boundary=execution_boundary,
        )
        audit.append("qde_public_validation_completed", {"result_id": result_id})

        return QDEPublicValidationResult(
            run_id=research_input.run_id,
            system=research_input.system,
            validation_profile=research_input.validation_profile,
            instrument_focus=research_input.instrument_focus,
            decisions=decision_tuple,
            scorecard=scorecard,
            execution_boundary=execution_boundary,
            audit_event_count=len(audit.events),
            result_id=result_id,
            deterministic_output=True,
        )

    def _evaluate_candidate(self, candidate: QDEValidationCandidate) -> QDEValidationDecision:
        if not candidate.source_feature_refs or not candidate.reference_level_refs:
            return _decision(candidate, QDEEvaluationStatus.REJECTED, QDEReasonCode.PROVENANCE_MISSING)
        if not candidate.no_lookahead_confirmed:
            return _decision(candidate, QDEEvaluationStatus.REJECTED, QDEReasonCode.NO_LOOKAHEAD_GUARD_FAILED)
        if not candidate.material_validation:
            return _decision(candidate, QDEEvaluationStatus.BLOCKED, QDEReasonCode.MATERIAL_VALIDATION_MISSING)
        if candidate.public_gate_score < self.minimum_public_gate_score:
            return _decision(candidate, QDEEvaluationStatus.REJECTED, QDEReasonCode.PUBLIC_GATE_SCORE_FAILED)
        return _decision(candidate, QDEEvaluationStatus.ACCEPTED, QDEReasonCode.CANDIDATE_ACCEPTED)


def _decision(
    candidate: QDEValidationCandidate,
    status: QDEEvaluationStatus,
    reason_code: QDEReasonCode,
) -> QDEValidationDecision:
    return QDEValidationDecision(
        candidate_id=candidate.candidate_id,
        family_id=candidate.family_id,
        side=candidate.side,
        status=status,
        reason_code=reason_code,
        public_gate_score=candidate.public_gate_score,
    )


def _result_id(
    *,
    run_id: str,
    decisions: tuple[QDEValidationDecision, ...],
    scorecard: QDEPortfolioSummary,
    execution_boundary: QDEExecutionBoundarySummary,
) -> str:
    body = {
        "run_id": run_id,
        "decisions": [decision.public_payload() for decision in decisions],
        "scorecard": scorecard.public_payload(),
        "execution_boundary": execution_boundary.public_payload(),
    }
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return "qde-result-" + hashlib.sha256(encoded).hexdigest()[:16]
