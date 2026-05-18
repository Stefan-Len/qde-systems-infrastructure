"""Fail-closed pre-trade risk policy for the execution showcase."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .market_state import MarketSnapshot, PortfolioState, SignalInstruction


class RiskReason(str, Enum):
    """Canonical risk reasons emitted by the sample policy."""

    ALLOWED = "allowed"
    LOW_CONFIDENCE = "low_confidence"
    MAX_OPEN_POSITIONS = "max_open_positions"
    DAILY_LOSS_LIMIT = "daily_loss_limit"
    VOLATILITY_OUT_OF_RANGE = "volatility_out_of_range"
    NOTIONAL_LIMIT = "notional_limit"


@dataclass(frozen=True)
class RiskPolicy:
    """Risk thresholds used before execution planning.

    Set max_total_notional to 0 to disable the notional cap in this sample.
    """

    min_confidence: float = 0.55
    max_open_positions: int = 1
    max_daily_loss_r: float = -3.0
    min_volatility_rank: float = 5.0
    max_volatility_rank: float = 95.0
    max_total_notional: float = 5_000_000.0
    contract_point_value: float = 50.0

    def validate(self) -> None:
        if not 0.0 <= self.min_confidence <= 1.0:
            raise ValueError("min_confidence must be in range 0..1")
        if self.max_open_positions < 0:
            raise ValueError("max_open_positions cannot be negative")
        if self.min_volatility_rank < 0.0 or self.max_volatility_rank > 100.0:
            raise ValueError("volatility rank bounds must stay in range 0..100")
        if self.min_volatility_rank > self.max_volatility_rank:
            raise ValueError("min_volatility_rank cannot exceed max_volatility_rank")
        if self.max_total_notional < 0:
            raise ValueError("max_total_notional cannot be negative")
        if self.contract_point_value <= 0:
            raise ValueError("contract_point_value must be positive")


@dataclass(frozen=True)
class RiskDecision:
    """Risk result consumed by the execution cycle."""

    allowed: bool
    reason: RiskReason
    detail: str


def evaluate_risk(
    *,
    market: MarketSnapshot,
    signal: SignalInstruction,
    portfolio: PortfolioState,
    policy: RiskPolicy,
) -> RiskDecision:
    """Evaluate pre-trade risk in a fixed order."""

    market.validate()
    signal.validate()
    portfolio.validate()
    policy.validate()

    if signal.confidence < policy.min_confidence:
        return RiskDecision(
            allowed=False,
            reason=RiskReason.LOW_CONFIDENCE,
            detail="signal confidence is below policy minimum",
        )

    if portfolio.open_positions >= policy.max_open_positions:
        return RiskDecision(
            allowed=False,
            reason=RiskReason.MAX_OPEN_POSITIONS,
            detail="open-position cap has been reached",
        )

    if portfolio.daily_loss_r <= policy.max_daily_loss_r:
        return RiskDecision(
            allowed=False,
            reason=RiskReason.DAILY_LOSS_LIMIT,
            detail="daily loss limit has been reached",
        )

    if not policy.min_volatility_rank <= market.volatility_rank <= policy.max_volatility_rank:
        return RiskDecision(
            allowed=False,
            reason=RiskReason.VOLATILITY_OUT_OF_RANGE,
            detail="market volatility is outside the configured range",
        )

    projected_notional = (
        portfolio.current_notional
        + signal.requested_contracts * market.last_price * policy.contract_point_value
    )
    if policy.max_total_notional > 0 and projected_notional > policy.max_total_notional:
        return RiskDecision(
            allowed=False,
            reason=RiskReason.NOTIONAL_LIMIT,
            detail="projected notional exceeds policy limit",
        )

    return RiskDecision(
        allowed=True,
        reason=RiskReason.ALLOWED,
        detail="risk policy allowed execution planning",
    )
