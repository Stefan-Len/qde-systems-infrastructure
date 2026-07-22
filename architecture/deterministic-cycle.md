# Deterministic Execution Cycle

This sample models one execution cycle with a fixed step order. It covers the runtime boundary around market state, signal intent, portfolio state, risk admission, execution planning, and audit evidence; market forecasting and broker integration are outside this repo.

## Cycle Order

1. Validate market state.
2. Validate signal instruction.
3. Validate portfolio state.
4. Evaluate pre-trade risk in fixed order.
5. Stop immediately if risk blocks the signal.
6. Build deterministic execution slices if risk allows the signal.
7. Append audit events for every material decision.

## Deterministic Identifiers

`client_order_id` values are derived from:

- `run_id`
- `signal_id`
- slice sequence number

This means the same cycle inputs produce the same planned order identifiers. That property is useful for replay, debugging, and idempotency design.

## Runtime Boundary

The sample stops at planning. A real broker adapter would be a separate boundary with its own contract, retries, reconciliation, and operational controls.
