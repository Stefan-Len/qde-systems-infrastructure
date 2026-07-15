from decimal import Decimal

from qde_systems_infrastructure import (
    QDECandidateSide,
    QDEEvaluationStatus,
    QDEPublicValidationPipeline,
    QDEReasonCode,
    QDESyntheticResearchInput,
    QDEValidationCandidate,
)


def _research_input() -> QDESyntheticResearchInput:
    return QDESyntheticResearchInput(
        run_id="qde-systems-public-validation-test",
        system="QDE-Systems Infrastructure",
        validation_profile="synthetic_qde_es_research_flow",
        instrument_focus="ES",
        generated_at_utc="2026-07-15T14:30:00Z",
    )


def _candidate(**overrides: object) -> QDEValidationCandidate:
    values = {
        "candidate_id": "qde-es-test-candidate",
        "family_id": "QDE_PUBLIC_LONG_RESEARCH_FAMILY",
        "side": QDECandidateSide.LONG,
        "decision_ts_event": "2026-07-15T14:31:00Z",
        "public_gate_score": Decimal("0.82"),
        "deterministic_order_key": "001",
        "source_feature_refs": ("synthetic_feature:long_context",),
        "reference_level_refs": ("synthetic_reference:session_high",),
        "session_context": "qde_public_ny_session_context",
        "cross_market_context": "qde_public_cross_market_context_available",
        "no_lookahead_confirmed": True,
        "material_validation": True,
    }
    values.update(overrides)
    return QDEValidationCandidate(**values)


def test_qde_public_pipeline_accepts_valid_candidate() -> None:
    result = QDEPublicValidationPipeline().run(
        research_input=_research_input(),
        candidates=(_candidate(),),
    )

    assert result.scorecard.accepted_count == 1
    assert result.decisions[0].status == QDEEvaluationStatus.ACCEPTED
    assert result.decisions[0].reason_code == QDEReasonCode.CANDIDATE_ACCEPTED
    assert result.execution_boundary.accepted_candidate_count == 1
    assert result.execution_boundary.broker_execution_included is False


def test_qde_public_pipeline_rejects_missing_provenance() -> None:
    result = QDEPublicValidationPipeline().run(
        research_input=_research_input(),
        candidates=(_candidate(source_feature_refs=()),),
    )

    assert result.scorecard.rejected_count == 1
    assert result.decisions[0].reason_code == QDEReasonCode.PROVENANCE_MISSING


def test_qde_public_pipeline_rejects_no_lookahead_failure() -> None:
    result = QDEPublicValidationPipeline().run(
        research_input=_research_input(),
        candidates=(_candidate(no_lookahead_confirmed=False),),
    )

    assert result.scorecard.rejected_count == 1
    assert result.decisions[0].reason_code == QDEReasonCode.NO_LOOKAHEAD_GUARD_FAILED


def test_qde_public_pipeline_blocks_missing_material_validation() -> None:
    result = QDEPublicValidationPipeline().run(
        research_input=_research_input(),
        candidates=(_candidate(material_validation=False),),
    )

    assert result.scorecard.blocked_count == 1
    assert result.decisions[0].reason_code == QDEReasonCode.MATERIAL_VALIDATION_MISSING


def test_qde_public_pipeline_rejects_below_public_placeholder_gate_score() -> None:
    result = QDEPublicValidationPipeline().run(
        research_input=_research_input(),
        candidates=(_candidate(public_gate_score=Decimal("0.64")),),
    )

    assert result.scorecard.rejected_count == 1
    assert result.decisions[0].reason_code == QDEReasonCode.PUBLIC_GATE_SCORE_FAILED
