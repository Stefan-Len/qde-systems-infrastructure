# Public Boundary

This repository is public on purpose, but it is narrow on purpose too.

It shows the shape of a QDE-Systems validation boundary:

- named research input;
- deterministic candidate ordering;
- provenance checks;
- no-lookahead guard;
- material validation gate;
- public risk gate;
- visible execution boundary without broker execution;
- count-based portfolio summary;
- audit trail.

It does not show the private QDE-Systems-ES strategy engine.

## Allowed In This Public Repo

- Synthetic QDE-style records.
- Public-safe reason codes.
- Deterministic sorting and result hashing.
- Validation gates that describe infrastructure discipline.
- A public risk gate summary.
- A visible execution boundary with no broker adapter.
- Count-based scorecard shape.
- Audit-chain mechanics.

## Not Allowed In This Public Repo

- Real historical market data.
- Private detector thresholds.
- Setup-family acceptance logic.
- Proprietary strategy rules.
- Broker adapter implementation.
- Account state or credentials.
- Topstep account detail.
- Performance, profit, funded-account, or LIVE-readiness claims.

The public sample should be useful to inspect, but it should not let a reader
reconstruct the private system.
