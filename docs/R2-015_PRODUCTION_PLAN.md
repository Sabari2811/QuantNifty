# R2-015 — Production Execution, Operations, Deployment & Live Certification

## Purpose

This document is the execution checklist for moving QuantNifty from validated live analytics to a production-ready, risk-controlled live trading system.

## Evidence baseline

- R2-014 canonical analytics-context architecture is complete.
- Latest verified full regression baseline: 479 passed, 1 skipped, 0 failed.
- Latest live validation completed 3 cycles with coverage, freshness, reconciliation, OI and Decision/Intelligence gates passing.
- Live option-chain integrity remains deliberately `SUSPECT`/`DEGRADED` where provider observations fail the intrinsic-value check. This is not treated as `VALID`.

## Work sequence

### 1. Execution contract
- Define canonical order intent and execution result models.
- Establish explicit direction/actionability/execution eligibility boundaries.
- Prevent direct UI-to-broker order paths.

### 2. Risk gate
- Validate market-data readiness, provenance, freshness and integrity policy.
- Enforce position limits, quantity limits and daily/trade risk limits.
- Enforce trading-block and kill-switch semantics.
- Make every rejection explicit and auditable.

### 3. Broker adapter
- Isolate broker-specific APIs behind a canonical execution interface.
- Support paper mode independently of live mode.
- Handle timeout, retry, rejection, partial fill and unknown-result states safely.

### 4. Order/position lifecycle
- Persist order intent and broker identifiers.
- Reconcile local and broker state.
- Make retries idempotent.
- Implement SL/target/trailing lifecycle only after canonical position state exists.

### 5. Operations
- Configuration and secret handling.
- Structured audit logging.
- Runtime health state.
- Provider disconnect/reconnect handling.
- Restart/recovery behavior.
- Alerts for actionable operational failures.

### 6. UI
- Validate production Streamlit runtime against canonical DashboardData.
- Show provenance/integrity/degraded states without inventing values.
- Ensure execution state is read-only from canonical backend state.

### 7. Certification
- Targeted regression after each change.
- Full regression before release gates.
- Multi-cycle paper execution.
- Failure/recovery simulations.
- End-to-end decision → risk → order intent → broker → position reconciliation.
- Final production-readiness gate.

### 8. Deployment
- Deploy only after certification gates pass.
- Verify production provider connectivity.
- Run post-deployment validation.
- Do not declare `LIVE` until actual deployed runtime evidence is captured.

## Guardrails

1. One change at a time.
2. Inspect implementation and tests before editing.
3. Preserve existing canonical architecture unless an audited gap requires change.
4. No fabricated, stale or silently substituted data.
5. Freshness and integrity remain independent.
6. `SUSPECT` must remain explicit.
7. Direction is not actionability.
8. Replay/history cannot silently veto a direction-consistent live decision.
9. Live execution must be impossible when the risk/data gate blocks it.
10. Deployment is not certification; certification requires runtime evidence.
