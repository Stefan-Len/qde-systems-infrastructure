from execution_infrastructure import (
    ExecutionCycle,
    MarketSnapshot,
    PortfolioState,
    RiskPolicy,
    RiskReason,
    SignalDirection,
    SignalInstruction,
    verify_audit_chain,
)


def test_blocked_cycle_does_not_produce_execution_plan() -> None:
    cycle = ExecutionCycle(run_id="run-1", policy=RiskPolicy(min_confidence=0.90))

    result = cycle.run(
        market=MarketSnapshot(
            symbol="ES",
            last_price=5250.0,
            volatility_rank=50.0,
            timestamp_utc="2026-05-18T12:00:00Z",
        ),
        signal=SignalInstruction(
            signal_id="sig-1",
            direction=SignalDirection.LONG,
            confidence=0.50,
            requested_contracts=1,
        ),
        portfolio=PortfolioState(
            open_positions=0,
            daily_loss_r=0.0,
            current_notional=0.0,
        ),
    )

    assert result.risk.reason == RiskReason.LOW_CONFIDENCE
    assert result.execution_plan is None
    assert result.audit_events[-1].event_type == "execution_blocked"
    assert verify_audit_chain(result.audit_events) is True


def test_allowed_cycle_produces_execution_plan_and_audit_chain() -> None:
    cycle = ExecutionCycle(run_id="run-1", policy=RiskPolicy(min_confidence=0.50))

    result = cycle.run(
        market=MarketSnapshot(
            symbol="ES",
            last_price=5250.0,
            volatility_rank=50.0,
            timestamp_utc="2026-05-18T12:00:00Z",
        ),
        signal=SignalInstruction(
            signal_id="sig-2",
            direction=SignalDirection.SHORT,
            confidence=0.80,
            requested_contracts=6,
        ),
        portfolio=PortfolioState(
            open_positions=0,
            daily_loss_r=0.0,
            current_notional=0.0,
        ),
    )

    assert result.execution_plan is not None
    assert [slice_.quantity for slice_ in result.execution_plan.slices] == [5, 1]
    assert result.audit_events[-1].event_type == "execution_planned"
    assert verify_audit_chain(result.audit_events) is True
