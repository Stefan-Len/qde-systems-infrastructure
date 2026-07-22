# Safety Boundaries

This repository keeps the safety model small and explicit.

## Fail-Closed Conditions

The execution cycle produces no execution plan when:

- signal confidence is below policy;
- open-position cap is reached;
- daily loss limit is reached;
- volatility rank is outside policy;
- projected notional exceeds policy.

## Audit Boundary

Every cycle writes structured audit events:

- `cycle_started`
- `risk_evaluated`
- `execution_blocked`
- `execution_planned`

The sample `AuditLedger` stores events in append order and links each record to the previous record through a SHA-256 hash. The verifier detects sequence breaks, previous-hash mismatches, and payload tampering.

## Scope Boundary

The README lists the full non-goals. In this document, the important safety boundary is narrower: execution planning ends before any broker call, credential use, external model request, or account-specific side effect.
