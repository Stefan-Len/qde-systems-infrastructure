"""One deterministic risk-gated execution cycle."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .audit_ledger import AuditEvent, AuditLedger
from .execution_plan import ExecutionPlan, build_execution_plan
from .market_state import MarketSnapshot, PortfolioState, SignalInstruction
from .risk_policy import RiskDecision, RiskPolicy, evaluate_risk


@dataclass(frozen=True)
class CycleResult:
    """Decision envelope returned by one execution cycle."""

    run_id: str
    risk: RiskDecision
    execution_plan: ExecutionPlan | None
    audit_events: tuple[AuditEvent, ...]


class ExecutionCycle:
    """Coordinate market, signal, risk, execution planning, and audit evidence."""

    def __init__(self, *, run_id: str, policy: RiskPolicy, ledger: AuditLedger | None = None) -> None:
        if not run_id.strip():
            raise ValueError("run_id is required")
        self.run_id = run_id
        self.policy = policy
        self.ledger = ledger or AuditLedger()

    def run(
        self,
        *,
        market: MarketSnapshot,
        signal: SignalInstruction,
        portfolio: PortfolioState,
    ) -> CycleResult:
        self.ledger.append(
            "cycle_started",
            {
                "run_id": self.run_id,
                "symbol": market.symbol,
                "signal_id": signal.signal_id,
            },
        )

        risk = evaluate_risk(
            market=market,
            signal=signal,
            portfolio=portfolio,
            policy=self.policy,
        )
        self.ledger.append(
            "risk_evaluated",
            {
                "allowed": risk.allowed,
                "reason": risk.reason.value,
                "detail": risk.detail,
            },
        )

        if not risk.allowed:
            self.ledger.append(
                "execution_blocked",
                {
                    "signal_id": signal.signal_id,
                    "reason": risk.reason.value,
                },
            )
            return CycleResult(
                run_id=self.run_id,
                risk=risk,
                execution_plan=None,
                audit_events=self.ledger.events,
            )

        plan = build_execution_plan(
            run_id=self.run_id,
            market=market,
            signal=signal,
        )
        self.ledger.append(
            "execution_planned",
            {
                "signal_id": plan.signal_id,
                "symbol": plan.symbol,
                "direction": plan.direction,
                "total_quantity": plan.total_quantity,
                "slices": [asdict(slice_) for slice_ in plan.slices],
            },
        )

        return CycleResult(
            run_id=self.run_id,
            risk=risk,
            execution_plan=plan,
            audit_events=self.ledger.events,
        )
