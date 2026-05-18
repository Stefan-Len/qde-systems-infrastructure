"""Run one deterministic execution-cycle example."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from execution_infrastructure import (  # noqa: E402
    ExecutionCycle,
    MarketSnapshot,
    PortfolioState,
    RiskPolicy,
    SignalDirection,
    SignalInstruction,
)


def main() -> None:
    cycle = ExecutionCycle(
        run_id="portfolio-demo-001",
        policy=RiskPolicy(
            min_confidence=0.60,
            max_open_positions=1,
            max_total_notional=2_500_000.0,
        ),
    )

    result = cycle.run(
        market=MarketSnapshot(
            symbol="ES",
            last_price=5250.25,
            volatility_rank=42.0,
            timestamp_utc="2026-05-18T12:00:00Z",
        ),
        signal=SignalInstruction(
            signal_id="sig-20260518-001",
            direction=SignalDirection.LONG,
            confidence=0.74,
            requested_contracts=7,
        ),
        portfolio=PortfolioState(
            open_positions=0,
            daily_loss_r=-0.5,
            current_notional=0.0,
        ),
    )

    print(json.dumps(asdict(result), indent=2, default=str))


if __name__ == "__main__":
    main()
