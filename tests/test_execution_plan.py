from execution_infrastructure import (
    MarketSnapshot,
    OrderType,
    SignalDirection,
    SignalInstruction,
    build_execution_plan,
)


def test_execution_plan_slices_quantity_deterministically() -> None:
    market = MarketSnapshot(
        symbol="ES",
        last_price=5250.0,
        volatility_rank=40.0,
        timestamp_utc="2026-05-18T12:00:00Z",
    )
    signal = SignalInstruction(
        signal_id="sig-abc",
        direction=SignalDirection.SHORT,
        confidence=0.80,
        requested_contracts=12,
    )

    first = build_execution_plan(
        run_id="run-1",
        market=market,
        signal=signal,
        max_contracts_per_slice=5,
    )
    second = build_execution_plan(
        run_id="run-1",
        market=market,
        signal=signal,
        max_contracts_per_slice=5,
    )

    assert [slice_.quantity for slice_ in first.slices] == [5, 5, 2]
    assert first == second
    assert [slice_.client_order_id for slice_ in first.slices] == [
        "coid-dee6f7eb8e578406",
        "coid-9615f41dfc241b0d",
        "coid-dbe7e9281069cd77",
    ]
    assert len({slice_.client_order_id for slice_ in first.slices}) == 3


def test_execution_plan_accepts_explicit_order_type_enum() -> None:
    market = MarketSnapshot(
        symbol="ES",
        last_price=5250.0,
        volatility_rank=40.0,
        timestamp_utc="2026-05-18T12:00:00Z",
    )
    signal = SignalInstruction(
        signal_id="sig-abc",
        direction=SignalDirection.SHORT,
        confidence=0.80,
        requested_contracts=1,
    )

    plan = build_execution_plan(
        run_id="run-1",
        market=market,
        signal=signal,
        order_type=OrderType.TWAP,
    )

    assert plan.slices[0].order_type == OrderType.TWAP
