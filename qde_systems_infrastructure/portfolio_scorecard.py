from __future__ import annotations

from dataclasses import dataclass

from .models import QDECandidateSide, QDEEvaluationStatus, QDEValidationDecision


@dataclass(frozen=True)
class QDEPortfolioSummary:
    candidate_count: int
    accepted_count: int
    rejected_count: int
    blocked_count: int
    long_candidate_count: int
    short_candidate_count: int

    @classmethod
    def from_decisions(cls, decisions: tuple[QDEValidationDecision, ...]) -> "QDEPortfolioSummary":
        return cls(
            candidate_count=len(decisions),
            accepted_count=sum(1 for decision in decisions if decision.status == QDEEvaluationStatus.ACCEPTED),
            rejected_count=sum(1 for decision in decisions if decision.status == QDEEvaluationStatus.REJECTED),
            blocked_count=sum(1 for decision in decisions if decision.status == QDEEvaluationStatus.BLOCKED),
            long_candidate_count=sum(1 for decision in decisions if decision.side == QDECandidateSide.LONG),
            short_candidate_count=sum(1 for decision in decisions if decision.side == QDECandidateSide.SHORT),
        )

    def public_payload(self) -> dict[str, int]:
        return {
            "candidate_count": self.candidate_count,
            "accepted_count": self.accepted_count,
            "rejected_count": self.rejected_count,
            "blocked_count": self.blocked_count,
            "long_candidate_count": self.long_candidate_count,
            "short_candidate_count": self.short_candidate_count,
        }
