# deterministic-execution-infrastructure
# Copyright (c) 2026 Stefan Len
# SPDX-License-Identifier: MIT
"""Market, signal, and portfolio state contracts for one execution cycle."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class SignalDirection(str, Enum):
    """Trade direction accepted by the execution planner."""

    LONG = "LONG"
    SHORT = "SHORT"


@dataclass(frozen=True)
class MarketSnapshot:
    """Minimal market state needed by the sample execution cycle."""

    symbol: str
    last_price: float
    volatility_rank: float
    timestamp_utc: str

    def validate(self) -> None:
        if not self.symbol.strip():
            raise ValueError("symbol is required")
        if self.last_price <= 0:
            raise ValueError("last_price must be positive")
        if not 0.0 <= self.volatility_rank <= 100.0:
            raise ValueError("volatility_rank must be in range 0..100")
        if not self.timestamp_utc.strip():
            raise ValueError("timestamp_utc is required")


@dataclass(frozen=True)
class SignalInstruction:
    """Model or strategy output after it has been reduced to an execution intent."""

    signal_id: str
    direction: SignalDirection
    confidence: float
    requested_contracts: int

    def validate(self) -> None:
        if not self.signal_id.strip():
            raise ValueError("signal_id is required")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be in range 0..1")
        if self.requested_contracts <= 0:
            raise ValueError("requested_contracts must be positive")


@dataclass(frozen=True)
class PortfolioState:
    """Portfolio state used by pre-trade risk admission."""

    open_positions: int
    daily_loss_r: float
    current_notional: float

    def validate(self) -> None:
        if self.open_positions < 0:
            raise ValueError("open_positions cannot be negative")
        if self.current_notional < 0:
            raise ValueError("current_notional cannot be negative")
