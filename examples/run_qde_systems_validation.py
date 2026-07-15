from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from qde_systems_infrastructure import (  # noqa: E402
    QDECandidateSide,
    QDEPublicValidationPipeline,
    QDESyntheticResearchInput,
    QDEValidationCandidate,
)


def build_qde_public_candidates() -> tuple[QDEValidationCandidate, ...]:
    return (
        QDEValidationCandidate(
            candidate_id="qde-es-public-candidate-003",
            family_id="QDE_PUBLIC_SHORT_RESEARCH_FAMILY",
            side=QDECandidateSide.SHORT,
            decision_ts_event="2026-07-15T14:37:00Z",
            public_gate_score=Decimal("0.64"),
            deterministic_order_key="003",
            source_feature_refs=("synthetic_feature:short_context",),
            reference_level_refs=("synthetic_reference:session_low",),
            session_context="qde_public_ny_session_context",
            cross_market_context="qde_public_cross_market_context_available",
            no_lookahead_confirmed=True,
            material_validation=True,
        ),
        QDEValidationCandidate(
            candidate_id="qde-es-public-candidate-001",
            family_id="QDE_PUBLIC_LONG_RESEARCH_FAMILY",
            side=QDECandidateSide.LONG,
            decision_ts_event="2026-07-15T14:31:00Z",
            public_gate_score=Decimal("0.82"),
            deterministic_order_key="001",
            source_feature_refs=("synthetic_feature:long_context",),
            reference_level_refs=("synthetic_reference:session_high",),
            session_context="qde_public_ny_session_context",
            cross_market_context="qde_public_cross_market_context_available",
            no_lookahead_confirmed=True,
            material_validation=True,
        ),
        QDEValidationCandidate(
            candidate_id="qde-es-public-candidate-004",
            family_id="QDE_PUBLIC_PORTFOLIO_REVIEW",
            side=QDECandidateSide.LONG,
            decision_ts_event="2026-07-15T14:40:00Z",
            public_gate_score=Decimal("0.91"),
            deterministic_order_key="004",
            source_feature_refs=("synthetic_feature:portfolio_context",),
            reference_level_refs=("synthetic_reference:session_high",),
            session_context="qde_public_ny_session_context",
            cross_market_context="qde_public_cross_market_context_available",
            no_lookahead_confirmed=True,
            material_validation=False,
        ),
        QDEValidationCandidate(
            candidate_id="qde-es-public-candidate-002",
            family_id="QDE_PUBLIC_LONG_RESEARCH_FAMILY",
            side=QDECandidateSide.LONG,
            decision_ts_event="2026-07-15T14:33:00Z",
            public_gate_score=Decimal("0.86"),
            deterministic_order_key="002",
            source_feature_refs=(),
            reference_level_refs=("synthetic_reference:session_high",),
            session_context="qde_public_ny_session_context",
            cross_market_context="qde_public_cross_market_context_available",
            no_lookahead_confirmed=True,
            material_validation=True,
        ),
    )


def main() -> None:
    research_input = QDESyntheticResearchInput(
        run_id="qde-systems-public-validation-001",
        system="QDE-Systems Infrastructure",
        validation_profile="synthetic_qde_es_research_flow",
        instrument_focus="ES",
        generated_at_utc="2026-07-15T14:30:00Z",
    )
    result = QDEPublicValidationPipeline().run(
        research_input=research_input,
        candidates=build_qde_public_candidates(),
    )
    print(json.dumps(result.public_summary(), indent=2))


if __name__ == "__main__":
    main()
