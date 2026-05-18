# deterministic-execution-infrastructure
# Copyright (c) 2026 Stefan Len
# SPDX-License-Identifier: MIT
"""Deterministic order planning and client-order-id generation."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import Enum

from .market_state import MarketSnapshot, SignalInstruction


class OrderType(str, Enum):
    """Order type accepted by the sample execution planner."""

    IOC = "IOC"
    TWAP = "TWAP"


@dataclass(frozen=True)
class ExecutionSlice:
    """One planned child order."""

    client_order_id: str
    quantity: int
    order_type: OrderType
    sequence: int


@dataclass(frozen=True)
class ExecutionPlan:
    """Execution plan produced after risk admission."""

    signal_id: str
    symbol: str
    direction: str
    total_quantity: int
    slices: tuple[ExecutionSlice, ...]


def _client_order_id(*, run_id: str, signal_id: str, sequence: int) -> str:
    material = f"{run_id}:{signal_id}:{sequence}".encode("utf-8")
    digest = hashlib.sha256(material).hexdigest()[:16]
    return f"coid-{digest}"


def build_execution_plan(
    *,
    run_id: str,
    market: MarketSnapshot,
    signal: SignalInstruction,
    max_contracts_per_slice: int = 5,
    order_type: OrderType = OrderType.IOC,
) -> ExecutionPlan:
    """Build a deterministic sliced execution plan."""

    if not run_id.strip():
        raise ValueError("run_id is required")
    market.validate()
    signal.validate()
    if max_contracts_per_slice <= 0:
        raise ValueError("max_contracts_per_slice must be positive")
    if not isinstance(order_type, OrderType):
        raise ValueError("order_type must be an OrderType")

    remaining = signal.requested_contracts
    slices: list[ExecutionSlice] = []
    sequence = 1
    while remaining > 0:
        quantity = min(remaining, max_contracts_per_slice)
        slices.append(
            ExecutionSlice(
                client_order_id=_client_order_id(
                    run_id=run_id,
                    signal_id=signal.signal_id,
                    sequence=sequence,
                ),
                quantity=quantity,
                order_type=order_type,
                sequence=sequence,
            )
        )
        remaining -= quantity
        sequence += 1

    return ExecutionPlan(
        signal_id=signal.signal_id,
        symbol=market.symbol,
        direction=signal.direction.value,
        total_quantity=signal.requested_contracts,
        slices=tuple(slices),
    )
