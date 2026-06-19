# qde-systems-infrastructure
# Copyright (c) 2026 Štefan Lengyel, trading as Stefan Len / QDE-Systems
# SPDX-License-Identifier: MIT
from execution_infrastructure import (
    MarketSnapshot,
    PortfolioState,
    RiskPolicy,
    RiskReason,
    SignalDirection,
    SignalInstruction,
    evaluate_risk,
)


def _market() -> MarketSnapshot:
    return MarketSnapshot(
        symbol="ES",
        last_price=5250.0,
        volatility_rank=50.0,
        timestamp_utc="2026-05-18T12:00:00Z",
    )


def _signal(confidence: float = 0.75, contracts: int = 1) -> SignalInstruction:
    return SignalInstruction(
        signal_id="sig-1",
        direction=SignalDirection.LONG,
        confidence=confidence,
        requested_contracts=contracts,
    )


def _portfolio(open_positions: int = 0, current_notional: float = 0.0) -> PortfolioState:
    return PortfolioState(
        open_positions=open_positions,
        daily_loss_r=-0.5,
        current_notional=current_notional,
    )


def test_low_confidence_signal_fails_closed() -> None:
    decision = evaluate_risk(
        market=_market(),
        signal=_signal(confidence=0.40),
        portfolio=_portfolio(),
        policy=RiskPolicy(min_confidence=0.60),
    )

    assert decision.allowed is False
    assert decision.reason == RiskReason.LOW_CONFIDENCE


def test_open_position_cap_blocks_execution() -> None:
    decision = evaluate_risk(
        market=_market(),
        signal=_signal(),
        portfolio=_portfolio(open_positions=1),
        policy=RiskPolicy(max_open_positions=1),
    )

    assert decision.allowed is False
    assert decision.reason == RiskReason.MAX_OPEN_POSITIONS


def test_notional_limit_blocks_projected_exposure() -> None:
    decision = evaluate_risk(
        market=_market(),
        signal=_signal(contracts=10),
        portfolio=_portfolio(current_notional=0.0),
        policy=RiskPolicy(max_total_notional=100_000.0),
    )

    assert decision.allowed is False
    assert decision.reason == RiskReason.NOTIONAL_LIMIT


def test_daily_loss_limit_blocks_execution() -> None:
    decision = evaluate_risk(
        market=_market(),
        signal=_signal(),
        portfolio=PortfolioState(
            open_positions=0,
            daily_loss_r=-3.5,
            current_notional=0.0,
        ),
        policy=RiskPolicy(max_daily_loss_r=-3.0),
    )

    assert decision.allowed is False
    assert decision.reason == RiskReason.DAILY_LOSS_LIMIT
