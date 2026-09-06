# QuantNifty — M0–M11 Progress Tracker

## Purpose

Persistent implementation, audit, validation and certification tracker for QuantNifty. This file is the continuity source for future chats. Every milestone, implementation change, regression result and certification decision must be recorded here.

## Operating contract

- Audit first; do not invent scope, data, mappings or evidence.
- Canonical backend/DashboardData is authoritative.
- UI must consume canonical data through approved adapters/presenters.
- No fabricated, silently substituted or stale values.
- Freshness and integrity remain independent.
- `SUSPECT` remains explicit and is never relabeled `VALID` without evidence.
- Direction and actionability remain separate.
- Historical/replay recommendations cannot silently veto a direction-consistent live decision.
- Gamma flip is regime/level evidence, not standalone BUY/SELL logic.
- IV skew directional mapping is a project heuristic.
- One change at a time.
- Inspect implementation and tests before editing.
- Targeted regression after every production behavior change.
- Full regression before release gates.
- Never run real-money order placement from tests.
- Deployment is not certification.
- Nothing is marked complete without evidence.
- Unavailable/unsupported behavior must have an explicit disposition.

## Current state

- Branch: `r2-011-canonical-snapshot-provenance`
- Current program: M0 — UI/backend inventory and gap audit
- R2-014 canonical analytics-context architecture: COMPLETE
- R2-015 production execution/certification program: IN PROGRESS
- Latest recorded full local regression baseline: 479 passed, 1 skipped, 0 failed
- Latest recorded live validation: 3 cycles; coverage/freshness/reconciliation/OI/decision-intelligence gates passed
- Live option-chain integrity: deliberately `SUSPECT`/`DEGRADED` where intrinsic-value validation fails; not treated as VALID
- Open tracking issues: R2-013 issue #12 and R2-015 issue #18

---

# Milestone checklist

## M0 — Baseline, inventory and audit lock

Status: IN PROGRESS

- [ ] Confirm exact branch/HEAD
- [ ] Inventory all Streamlit/UI entry points
- [ ] Inventory UI components/pages
- [ ] Inventory UI adapters/presenters
- [ ] Inventory canonical `DashboardData` models
- [ ] Inventory backend-produced fields
- [ ] Inventory every UI-rendered field
- [ ] Map provider → canonical backend → DashboardData → adapter → UI
- [ ] Identify UI-side calculations/recomputation
- [ ] Identify hardcoded/default/fallback values
- [ ] Identify stale/legacy UI paths
- [ ] Identify missing backend fields
- [ ] Identify unused backend capabilities
- [ ] Create complete UI/backend gap matrix
- [ ] Assign every item: VALIDATED / FIX REQUIRED / INTENTIONALLY UNAVAILABLE / UNSUPPORTED
- [ ] Record audit evidence and commit SHA

Exit gate: zero unexplained UI surfaces or fields.

## M1 — Canonical Dashboard contract

Status: NOT STARTED

- [ ] Spot
- [ ] Expiry
- [ ] Option chain
- [ ] Strike
- [ ] CE/PE LTP
- [ ] Bid/ask
- [ ] OI
- [ ] OI change
- [ ] Volume
- [ ] IV
- [ ] Greeks
- [ ] GEX
- [ ] DEX
- [ ] Gamma walls
- [ ] Gamma flip
- [ ] Expected move
- [ ] Max pain
- [ ] PCR
- [ ] IV skew
- [ ] Dealer flow
- [ ] Market structure
- [ ] Direction
- [ ] Actionability
- [ ] Decision
- [ ] Intelligence/reason
- [ ] Confidence/scoring
- [ ] Provenance
- [ ] Freshness
- [ ] Integrity
- [ ] Coverage
- [ ] Missing-contract information
- [ ] Degraded-data state
- [ ] Execution state
- [ ] Position state
- [ ] Recovery state
- [ ] Reconciliation state
- [ ] Complete field-level mapping

Exit gate: zero unexplained dashboard fields.

## M2 — UI/backend divergence elimination

Status: NOT STARTED

- [ ] Remove duplicate UI calculations where canonical backend exists
- [ ] Remove stale/duplicate adapters
- [ ] Fix field-name mismatches
- [ ] Fix type mismatches
- [ ] Fix enum/status mismatches
- [ ] Fix missing-value handling
- [ ] Fix fallback semantics
- [ ] Prevent fabricated values
- [ ] Preserve UNKNOWN
- [ ] Preserve SUSPECT
- [ ] Preserve INVALID
- [ ] Preserve freshness separately from integrity
- [ ] Preserve direction/actionability separation
- [ ] Prevent history/replay from silently vetoing live decisions
- [ ] Add regression coverage for every correction

Exit gate: canonical backend is the sole authoritative source for displayed values.

## M3 — Live option-chain UI certification

Status: NOT STARTED

- [ ] Live expiry
- [ ] Live spot
- [ ] Expected contract count
- [ ] Received contract count
- [ ] Missing contracts
- [ ] Provider observation timestamp
- [ ] Freshness
- [ ] Integrity
- [ ] Integrity reason
- [ ] Bid/ask handling
- [ ] OI/OI-change handling
- [ ] Partial response handling
- [ ] No stale-as-fresh display
- [ ] No synthetic timestamp
- [ ] No silent contract substitution

Exit gate: live option-chain UI matches canonical live DashboardData.

## M4 — Analytics/intelligence UI certification

Status: NOT STARTED

- [ ] Greeks
- [ ] GEX
- [ ] DEX
- [ ] Gamma walls
- [ ] Gamma flip
- [ ] Expected move
- [ ] Max pain
- [ ] PCR
- [ ] IV skew
- [ ] Dealer flow
- [ ] Market structure
- [ ] Direction
- [ ] Actionability
- [ ] Decision
- [ ] Intelligence explanation
- [ ] Gamma flip remains regime/level evidence
- [ ] IV skew heuristic remains explicit
- [ ] WAIT remains possible and non-vetoing where appropriate
- [ ] Historical/replay recommendations cannot silently veto live direction

Exit gate: UI semantics exactly match canonical backend semantics.

## M5 — Provenance/data-quality UI

Status: NOT STARTED

- [ ] Source/provider
- [ ] Observation timestamp
- [ ] Processing timestamp
- [ ] Freshness
- [ ] Coverage
- [ ] Missing count
- [ ] Integrity
- [ ] Integrity reason
- [ ] Freshness reason
- [ ] Degraded state
- [ ] Provider failure
- [ ] Partial data
- [ ] Clock skew
- [ ] Structural invalidity
- [ ] SUSPECT representation
- [ ] INVALID representation
- [ ] No generic green/live indicator when canonical state is degraded

Exit gate: user can understand why displayed data is trusted or degraded.

## M6 — Decision → execution UI

Status: NOT STARTED

- [ ] Execution intent
- [ ] Client order ID
- [ ] Symbol
- [ ] Option type
- [ ] Strike
- [ ] Quantity
- [ ] Action
- [ ] Limit price
- [ ] Risk decision
- [ ] Risk block reason
- [ ] Kill-switch state
- [ ] Execution status
- [ ] Broker order ID
- [ ] Filled quantity
- [ ] Average fill
- [ ] Execution reason
- [ ] Retry/reconciliation state
- [ ] Paper/live mode
- [ ] No accidental live-order control
- [ ] Rejected state
- [ ] UNKNOWN/SUBMITTED states

Exit gate: UI accurately represents canonical execution state and never bypasses safety boundaries.

## M7 — Position/recovery UI

Status: NOT STARTED

- [ ] Open position
- [ ] Entry price
- [ ] Current price
- [ ] Quantity
- [ ] Stop loss
- [ ] Target
- [ ] Trailing stop
- [ ] Position status
- [ ] Broker order identity
- [ ] Client order identity
- [ ] Persisted state
- [ ] Recovery state
- [ ] Reconciliation state
- [ ] Manual-resolution requirement
- [ ] Restart/recovery block
- [ ] No inferred broker position

Exit gate: position state remains auditable through restart/recovery.

## M8 — Failure/degraded-state UI certification

Status: NOT STARTED

- [ ] Provider unavailable
- [ ] Spot unavailable
- [ ] Option chain incomplete
- [ ] Stale quote
- [ ] SUSPECT quote
- [ ] INVALID quote
- [ ] Missing contracts
- [ ] Partial provider response
- [ ] Analytics unavailable
- [ ] Decision unavailable
- [ ] Risk blocked
- [ ] Kill switch active
- [ ] Broker rejection
- [ ] Broker timeout
- [ ] UNKNOWN execution
- [ ] Reconciliation mismatch
- [ ] Recovery unavailable
- [ ] Persistence unavailable
- [ ] Every runtime state has defined UI disposition

Exit gate: no undefined runtime state reaches UI.

## M9 — UI automated regression

Status: NOT STARTED

- [ ] DashboardData → adapter tests
- [ ] Adapter → UI tests
- [ ] Field completeness tests
- [ ] No-recomputation tests
- [ ] Provenance tests
- [ ] Freshness tests
- [ ] Integrity tests
- [ ] Degraded-state tests
- [ ] Decision tests
- [ ] Execution-state tests
- [ ] Position-state tests
- [ ] Recovery-state tests
- [ ] Full regression

Exit gate: UI contract is automatically protected.

## M10 — End-to-end certification

Status: NOT STARTED

- [ ] Provider → canonical snapshot
- [ ] Canonical snapshot → analytics
- [ ] Analytics → decision
- [ ] Decision → intelligence
- [ ] Intelligence → DashboardData
- [ ] DashboardData → UI
- [ ] Decision → execution intent
- [ ] Intent → risk gate
- [ ] Risk → broker adapter
- [ ] Broker → execution result
- [ ] Result → audit
- [ ] Result → position state
- [ ] Position → recovery/reconciliation
- [ ] Recovery/reconciliation → UI
- [ ] One complete cycle
- [ ] Multiple consecutive cycles
- [ ] Degraded cycle
- [ ] Recovery cycle
- [ ] Reconciliation cycle
- [ ] Paper execution cycle
- [ ] Execution rejection cycle
- [ ] Partial/ambiguous execution cycle
- [ ] No stale-state leakage
- [ ] No duplicate order
- [ ] No UI/backend divergence

Exit gate: complete end-to-end evidence exists.

## M11 — Final production readiness and deployment certification

Status: NOT STARTED

- [ ] Full regression
- [ ] Live market validation
- [ ] Live UI validation
- [ ] Execution validation
- [ ] Recovery validation
- [ ] Reconciliation validation
- [ ] Configuration validation
- [ ] Secret handling validation
- [ ] Structured logging
- [ ] Runtime health monitoring
- [ ] Alerting
- [ ] Restart validation
- [ ] Deployment validation
- [ ] Post-deployment validation
- [ ] Evidence bundle
- [ ] Final production-readiness gate
- [ ] Final LIVE certification

Exit gate: evidence-backed production certification only. Deployment alone never changes status to LIVE.

---

# Backend → UI mapping register

Every field discovered during M0 must be entered here with its authoritative source, adapter, UI destination, semantic contract, validation evidence and disposition.

| Domain | Backend source | Canonical field | Adapter/presenter | UI destination | Status | Evidence/commit |
|---|---|---|---|---|---|---|
| Spot | TBD by M0 audit | TBD | TBD | TBD | PENDING | — |
| Expiry | TBD by M0 audit | TBD | TBD | TBD | PENDING | — |
| Option chain | TBD by M0 audit | TBD | TBD | TBD | PENDING | — |
| Greeks | TBD by M0 audit | TBD | TBD | TBD | PENDING | — |
| GEX/DEX | TBD by M0 audit | TBD | TBD | TBD | PENDING | — |
| Gamma walls/flip | TBD by M0 audit | TBD | TBD | TBD | PENDING | — |
| Expected move/Max Pain/PCR | TBD by M0 audit | TBD | TBD | TBD | PENDING | — |
| IV skew/dealer flow | TBD by M0 audit | TBD | TBD | TBD | PENDING | — |
| Market structure | TBD by M0 audit | TBD | TBD | TBD | PENDING | — |
| Direction/actionability | TBD by M0 audit | TBD | TBD | TBD | PENDING | — |
| Decision/intelligence | TBD by M0 audit | TBD | TBD | TBD | PENDING | — |
| Provenance/freshness/integrity | TBD by M0 audit | TBD | TBD | TBD | PENDING | — |
| Execution | TBD by M0 audit | TBD | TBD | TBD | PENDING | — |
| Position/recovery | TBD by M0 audit | TBD | TBD | TBD | PENDING | — |

No `TBD` entry may remain at the end of M1.

# Progress log

## Tracker initialization

- Status: COMPLETE
- Program: M0–M11
- Tracker created on `r2-011-canonical-snapshot-provenance`
- Commit: recorded by GitHub create-file operation
- Next action: M0 UI/backend inventory audit

## Per-commit update contract

For every implementation commit, append an entry containing:

1. Date/time
2. Milestone
3. Change summary
4. Files changed
5. Targeted tests and result
6. Full regression result when applicable
7. Live evidence when applicable
8. Commit SHA
9. Checklist items completed
10. Remaining gaps
11. Exact next action

## Final status rule

The program is complete only when M0–M11 are all closed with evidence and the final production-readiness gate explicitly records certification. Any unresolved item must remain visible with a reason and disposition; nothing is silently dropped.
