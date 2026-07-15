from decimal import Decimal

from qde_systems_infrastructure import (
    QDECandidateSide,
    QDEPublicValidationPipeline,
    QDESyntheticResearchInput,
    QDEValidationCandidate,
)


def _research_input() -> QDESyntheticResearchInput:
    return QDESyntheticResearchInput(
        run_id="qde-systems-deterministic-test",
        system="QDE-Systems Infrastructure",
        validation_profile="synthetic_qde_es_research_flow",
        instrument_focus="ES",
        generated_at_utc="2026-07-15T14:30:00Z",
    )


def _candidate(candidate_id: str, order_key: str) -> QDEValidationCandidate:
    return QDEValidationCandidate(
        candidate_id=candidate_id,
        family_id="QDE_PUBLIC_LONG_RESEARCH_FAMILY",
        side=QDECandidateSide.LONG,
        decision_ts_event="2026-07-15T14:31:00Z",
        public_gate_score=Decimal("0.82"),
        deterministic_order_key=order_key,
        source_feature_refs=("synthetic_feature:long_context",),
        reference_level_refs=("synthetic_reference:session_high",),
        session_context="qde_public_ny_session_context",
        cross_market_context="qde_public_cross_market_context_available",
        no_lookahead_confirmed=True,
        material_validation=True,
    )


def test_qde_public_result_id_is_stable_across_input_order() -> None:
    pipeline = QDEPublicValidationPipeline()
    first = pipeline.run(
        research_input=_research_input(),
        candidates=(
            _candidate("qde-es-candidate-002", "002"),
            _candidate("qde-es-candidate-001", "001"),
        ),
    )
    second = pipeline.run(
        research_input=_research_input(),
        candidates=(
            _candidate("qde-es-candidate-001", "001"),
            _candidate("qde-es-candidate-002", "002"),
        ),
    )

    assert first.result_id == second.result_id
    assert [decision.candidate_id for decision in first.decisions] == [
        "qde-es-candidate-001",
        "qde-es-candidate-002",
    ]
