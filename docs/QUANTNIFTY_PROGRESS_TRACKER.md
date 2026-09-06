# QuantNifty — Master Project Tracker, Summary & Architecture

## 1. Project summary

QuantNifty is a modular NIFTY options analytics, decision-intelligence, paper/live-execution and certification platform.

**Current objective:** move from validated live analytics into a fully auditable, risk-controlled production system without bypassing canonical backend contracts.

**Current branch:** `r2-011-canonical-snapshot-provenance`  
**Current phase:** M0 — UI/backend inventory and gap audit  
**Program:** R2-015 — Production Execution, Operations, Deployment & Live Certification

### Evidence baseline
- R2-014 canonical analytics-context architecture: **COMPLETE**
- Latest recorded full local regression baseline: **479 passed, 1 skipped, 0 failed**
- Latest recorded live validation: **3 cycles**, with coverage/freshness/reconciliation/OI/Decision-Intelligence gates passing
- Live option-chain integrity: deliberately **SUSPECT/DEGRADED** where intrinsic-value validation fails; never relabeled VALID without evidence
- R2-013 issue #12: **OPEN**
- R2-015 issue #18: **OPEN**

---

# 2. Architecture

## 2.1 Canonical market-data and intelligence flow

```text
INDMoney / INDstocks Provider
        │
        ▼
Provider adapters / normalization
        │
        ▼
Canonical market snapshot + provenance
        │
        ├── Spot / expiry / option chain
        ├── Coverage / missing contracts
        ├── Freshness / freshness reason
        └── Integrity / integrity reason
        │
        ▼
Analytics Pipeline
        │
        ▼
Canonical MarketContext / analytics
        │
        ├── Greeks
        ├── GEX / DEX
        ├── Gamma walls / flip
        ├── Expected Move
        ├── Max Pain / PCR
        ├── IV skew
        ├── Dealer flow
        └── Market structure
        │
        ▼
Decision Engine
        │
        ├── Direction
        ├── Actionability
        └── Decision
        │
        ▼
Intelligence / explanation / consistency
        │
        ▼
Canonical DashboardData
        │
        ▼
Dashboard adapters / presenters
        │
        ▼
Streamlit UI
```

## 2.2 Canonical execution flow

```text
Canonical Decision
      │
      ▼
Order Intent Factory
      │
      ▼
Canonical OrderIntent
      │
      ▼
Risk / market-data readiness gate
      │
      ├── blocked → canonical REJECTED result + audit
      │
      ▼
Runtime safety gates
      │
      ├── kill switch
      ├── reconciliation
      └── execution-mode boundary
      │
      ▼
Paper or live execution adapter
      │
      ▼
Canonical ExecutionResult
      │
      ├── EXECUTED / SUBMITTED / REJECTED / FAILED / UNKNOWN
      │
      ├──────────────► Execution audit store
      │
      └──────────────► Position state / lifecycle
                              │
                              ▼
                       Recovery / reconciliation
                              │
                              ▼
                         Canonical runtime
                              │
                              ▼
                              UI
```

## 2.3 Position/recovery flow

```text
Paper/Canonical Position
        │
        ▼
PositionState
        │
        ▼
SQLitePositionStateStore
        │
        ▼
PositionRuntimeService
        │
        ├── lifecycle evaluation
        ├── persistence
        └── runtime recovery
        │
        ▼
Position reconciliation
        │
        ├── MATCH → continuation allowed
        ├── MISMATCH → manual resolution
        └── UNKNOWN → continuation blocked
```

## 2.4 Shared runtime boundary

`RuntimeContext` is the shared runtime boundary for market data, canonical typed analytics, decision/intelligence, execution, position, recovery and reconciliation state.

Canonical state includes `market_context`, `analytics`, `data_provenance`, `decision`, `intelligence`, `execution_intent`, `execution_result`, `execution_lifecycle`, `position_recovery`, `position_reconciliation`, risk state and runtime status.

---

# 3. Architecture guardrails

1. Audit first; never invent scope, data, mappings or evidence.
2. Canonical backend/DashboardData is authoritative.
3. UI consumes canonical data through approved adapters/presenters.
4. No fabricated, silently substituted or stale values.
5. Freshness and integrity are independent.
6. `SUSPECT` and `INVALID` remain explicit.
7. Direction and actionability remain separate.
8. Historical/replay recommendations cannot silently veto a direction-consistent live decision.
9. Gamma flip is regime/level evidence, not standalone BUY/SELL logic.
10. IV skew directional mapping is a project heuristic.
11. One change at a time.
12. Inspect implementation and tests before editing.
13. Targeted regression after every production behavior change.
14. Full regression before release gates.
15. Never run real-money order placement from tests.
16. Unknown/ambiguous broker outcomes require reconciliation; blind retry is prohibited.
17. Live execution must be impossible when safety/data gates block it.
18. Deployment is not certification.
19. Nothing is marked complete without evidence.
20. Every unsupported/unavailable capability receives an explicit disposition.

---

# 4. Master milestone tracker

## M0 — Baseline, inventory and audit lock
**Status: IN PROGRESS**

- [x] Confirm exact branch/HEAD
- [x] Inventory all Streamlit/UI entry points
- [x] Inventory UI components/pages
- [x] Inventory UI adapters/presenters
- [ ] Inventory canonical DashboardData models
- [ ] Inventory backend-produced fields
- [ ] Inventory every UI-rendered field
- [ ] Map provider → canonical backend → DashboardData → adapter → UI
- [ ] Identify UI-side calculations/recomputation
- [ ] Identify hardcoded/default/fallback values
- [x] Identify stale/legacy UI paths
- [ ] Identify missing backend fields
- [ ] Identify unused backend capabilities
- [ ] Create complete UI/backend gap matrix
- [ ] Assign every item VALIDATED / FIX REQUIRED / INTENTIONALLY UNAVAILABLE / UNSUPPORTED
- [ ] Record audit evidence and commit SHA

### M0 boundary B1 — Exact branch / HEAD confirmation
**Status: COMPLETE**

- Verified branch: `r2-011-canonical-snapshot-provenance`
- Verified HEAD before tracker update: `74e43edbf6ff560c6126e58531aa6218dba69311`
- Verification source: GitHub branch ref `refs/heads/r2-011-canonical-snapshot-provenance`
- Verification date: 2026-09-06
- Scope: repository identity only; no local working-tree state inferred or changed.
- Boundary commit: `af9ede4b021a7c8024208aec888b790df9e8ab60`

### M0 boundary B2 — Streamlit/UI entry-point and legacy-path inventory
**Status: COMPLETE**

- Primary Streamlit entry point: `dashboard/app.py`.
- Legacy application entry point: `app/app.py`.
- Legacy application page set: `app/pages/dashboard.py`, `portfolio.py`, `performance.py`, `journal.py`, `option_chain.py`, `replay.py`, `runtime.py`, `institutional.py`, with `strategy.py` currently empty.
- `app/app.py` remains a reachable Streamlit entry point and routes its Dashboard page through `app/pages/dashboard.py`.
- `app/pages/dashboard.py` uses `app.services.LiveService` for runtime context, but `LiveService` is explicitly documented and implemented as a compatibility adapter over the single canonical `RuntimeManager`; it is not a second market-data acquisition owner.
- Active canonical dashboard path is `dashboard/app.py` → `DashboardController` → `RuntimeManager` → `DashboardData` → dashboard components.
- Legacy path is therefore classified **LEGACY / COMPATIBILITY**, not deleted or treated as a second canonical runtime.
- Evidence files inspected: `dashboard/app.py`, `app/app.py`, `app/pages/dashboard.py`, `app/services/live_service.py`.
- Boundary date: 2026-09-06.
- Boundary commit: `a321bfc9a3fc47c065f74c35b16cfa2055b0660f`.

### M0 boundary B3 — UI adapter / presenter inventory
**Status: COMPLETE**

Canonical dashboard adapters/presenters identified and traced:
- `dashboard/decision_adapter.py` — maps `DashboardData.signal`, `DashboardData.probability`, and `DashboardData.trade_plan` into the shared decision UI contract; confidence is sourced from canonical decision signal, not probability.
- `dashboard/intelligence_adapter.py` — maps typed `IntelligenceResult` into UI-safe intelligence, scenario, historical-evidence, regime, data-quality, freshness and integrity payloads.
- `dashboard/market_summary_adapter.py` — maps spot/expiry/expected-move/PCR/Max-Pain directly from `DashboardData` with no analytics recomputation.
- `dashboard/provenance_adapter.py` — maps runtime acquisition provenance, coverage, freshness and integrity states; option-chain quality remains READY/DEGRADED/UNAVAILABLE.
- `dashboard/ui_runtime_contract.py` — audit-only orchestration contract used by the real Streamlit entrypoint test; it reuses the canonical decision and market-summary adapters and passes through intelligence/provenance/integrity/option-chain/Greeks values from the same `DashboardData` cycle.
- `dashboard/decision_intelligence_status.py` — canonical Decision ↔ Intelligence consistency mapping used by `DashboardController`.
- `dashboard/dashboard_controller.py` is the primary backend-to-UI projection boundary, constructing `DashboardData` from `RuntimeContext.market_context` while retaining `ctx.analytics` only as the established generic compatibility/display projection.
- The Streamlit entrypoint `dashboard/app.py` calls the canonical adapters/presenters and records the exact values used at the UI boundary through `_quantnifty_ui_contract` for runtime regression.

Legacy presentation remains under `app/components/*`; the legacy dashboard consumes the canonical runtime through `LiveService`. No legacy presenter was deleted in this audit.

Evidence files inspected: `dashboard/decision_adapter.py`, `dashboard/intelligence_adapter.py`, `dashboard/market_summary_adapter.py`, `dashboard/provenance_adapter.py`, `dashboard/ui_runtime_contract.py`, `dashboard/decision_intelligence_status.py`, `dashboard/dashboard_controller.py`, `dashboard/app.py`.
Evidence: `tests/test_streamlit_runtime_ui_contract.py` exercises the real `dashboard/app.py` entrypoint with deterministic `DashboardData` and validates the emitted UI contract.
Boundary date: 2026-09-06.
Boundary commit: recorded in tracker update following B3.

**Next action:** inventory canonical `DashboardData` models and fields against the adapter inputs.

**Exit gate:** zero unexplained UI surfaces or fields.

## M1 — Canonical Dashboard contract
**Status: NOT STARTED**

- [ ] Spot / expiry / option chain
- [ ] Strike / CE / PE LTP / bid / ask
- [ ] OI / OI change / volume / IV
- [ ] Greeks / GEX / DEX / gamma walls / gamma flip
- [ ] Expected move / Max Pain / PCR
- [ ] IV skew / dealer flow / market structure
- [ ] Direction / actionability / decision
- [ ] Intelligence / confidence / scoring
- [ ] Provenance / freshness / integrity / coverage
- [ ] Missing-contract / degraded-data state
- [ ] Execution / position / recovery / reconciliation state
- [ ] Complete field-level mapping

## M2 — UI/backend divergence elimination
**Status: NOT STARTED**

- [ ] Remove duplicate UI calculations
- [ ] Remove stale/duplicate adapters
- [ ] Fix field/type/enum mismatches
- [ ] Fix missing-value/fallback semantics
- [ ] Prevent fabricated values
- [ ] Preserve UNKNOWN / SUSPECT / INVALID
- [ ] Preserve freshness separately from integrity
- [ ] Preserve direction/actionability separation
- [ ] Prevent history/replay vetoes
- [ ] Regression coverage for every correction

## M3 — Live option-chain UI certification
**Status: NOT STARTED**

- [ ] Live expiry/spot
- [ ] Expected/received/missing contracts
- [ ] Provider observation timestamp
- [ ] Freshness/integrity/reasons
- [ ] Bid/ask/OI/OI-change
- [ ] Partial response handling
- [ ] No stale-as-fresh display
- [ ] No synthetic timestamp
- [ ] No silent substitution

## M4 — Analytics/intelligence UI certification
**Status: NOT STARTED**

- [ ] All analytics fields and semantics
- [ ] Direction/actionability/decision
- [ ] Intelligence explanation
- [ ] Gamma flip semantics
- [ ] IV skew heuristic semantics
- [ ] WAIT behavior
- [ ] Historical/replay isolation

## M5 — Provenance/data-quality UI
**Status: NOT STARTED**

- [ ] Source/provider
- [ ] Observation/processing timestamps
- [ ] Freshness/freshness reason
- [ ] Coverage/missing count
- [ ] Integrity/integrity reason
- [ ] Degraded/provider-failure/partial states
- [ ] Clock skew/structural invalidity
- [ ] SUSPECT/INVALID representation

## M6 — Decision → execution UI
**Status: NOT STARTED**

- [ ] Intent/client ID
- [ ] Instrument/action/quantity/price
- [ ] Risk decision/block reason
- [ ] Kill-switch state
- [ ] Execution status/broker ID/fills
- [ ] Retry/reconciliation state
- [ ] Paper/live mode
- [ ] No accidental live-order control

## M7 — Position/recovery UI
**Status: NOT STARTED**

- [ ] Position state/lifecycle
- [ ] Entry/current/SL/target/trailing
- [ ] Client/broker identities
- [ ] Persisted state
- [ ] Recovery/reconciliation
- [ ] Manual-resolution requirement
- [ ] Restart block
- [ ] No inferred broker position

## M8 — Failure/degraded-state UI certification
**Status: NOT STARTED**

- [ ] Provider/spot/chain unavailable
- [ ] Stale/SUSPECT/INVALID
- [ ] Partial/missing data
- [ ] Analytics/decision unavailable
- [ ] Risk/kill-switch blocked
- [ ] Broker rejection/timeout/UNKNOWN
- [ ] Reconciliation mismatch
- [ ] Recovery/persistence unavailable
- [ ] Every runtime state has UI disposition

## M9 — UI automated regression
**Status: NOT STARTED**

- [ ] DashboardData → adapter
- [ ] Adapter → UI
- [ ] Field completeness
- [ ] No recomputation
- [ ] Provenance/freshness/integrity
- [ ] Degraded states
- [ ] Decision/execution/position/recovery states
- [ ] Full regression

## M10 — End-to-end certification
**Status: NOT STARTED**

- [ ] Provider → canonical snapshot
- [ ] Snapshot → analytics → decision → intelligence
- [ ] Intelligence → DashboardData → UI
- [ ] Decision → intent → risk → broker → result
- [ ] Result → audit → position → recovery/reconciliation → UI
- [ ] Complete cycle
- [ ] Multiple cycles
- [ ] Degraded/recovery/reconciliation cycles
- [ ] Paper execution/rejection/ambiguous execution
- [ ] No stale leakage
- [ ] No duplicate order
- [ ] No UI/backend divergence

## M11 — Production readiness and deployment certification
**Status: NOT STARTED**

- [ ] Full regression
- [ ] Live market/UI validation
- [ ] Execution/recovery/reconciliation validation
- [ ] Configuration/secrets validation
- [ ] Structured logging/health/alerts
- [ ] Restart validation
- [ ] Deployment/post-deployment validation
- [ ] Evidence bundle
- [ ] Production-readiness gate
- [ ] Final LIVE certification

**Exit gate:** evidence-backed production certification only.

---

# 5. Backend → UI mapping register

| Domain | Canonical source | Adapter/presenter | UI | Status | Evidence |
|---|---|---|---|---|---|
| Spot | M0 audit | Pending | Pending | PENDING | — |
| Expiry | M0 audit | Pending | Pending | PENDING | — |
| Option chain | M0 audit | Pending | Pending | PENDING | — |
| Greeks | M0 audit | Pending | Pending | PENDING | — |
| GEX / DEX | M0 audit | Pending | Pending | PENDING | — |
| Gamma walls / flip | M0 audit | Pending | Pending | PENDING | — |
| Expected Move / Max Pain / PCR | M0 audit | Pending | Pending | PENDING | — |
| IV skew / dealer flow | M0 audit | Pending | Pending | PENDING | — |
| Market structure | M0 audit | Pending | Pending | PENDING | — |
| Direction / actionability | M0 audit | Pending | Pending | PENDING | — |
| Decision / intelligence | M0 audit | Pending | Pending | PENDING | — |
| Provenance / freshness / integrity | M0 audit | Pending | Pending | PENDING | — |
| Execution | Canonical execution contract | Pending | Pending | PENDING | — |
| Position / recovery / reconciliation | Canonical position state | Pending | Pending | PENDING | — |

No unresolved `TBD`/`PENDING` entry may remain after the relevant milestone exit gate.

---

# 6. Implementation evidence register

| Area | Evidence | Status |
|---|---|---|
| Canonical execution contract | `execution/execution_contract.py` + tests | VALIDATED |
| Risk/data readiness gate | `risk/risk_manager.py` + targeted tests | VALIDATED |
| Execution safety boundary | TradeExecutionPipeline + safety tests | VALIDATED |
| Order intent | `execution/order_intent_factory.py` + tests | VALIDATED |
| Idempotency | `execution/idempotency.py` + tests | VALIDATED |
| Paper execution adapter | `execution/paper_execution_adapter.py` + tests | VALIDATED |
| Execution lifecycle | `execution/execution_lifecycle.py` + tests | VALIDATED |
| Live INDMoney adapter | resolver/mapper/result mapper/live adapter + tests | VALIDATED at targeted-contract level |
| Live runtime safety | kill switch + reconciliation runtime gates + tests | VALIDATED at targeted-contract level |
| Execution audit persistence | In-memory + SQLite stores + tests | VALIDATED |
| Execution recovery | recovery decisions/runtime wiring + tests | VALIDATED at targeted-test level |
| Canonical position state | `execution/position_state.py` + 14 tests | VALIDATED |
| Position lifecycle | lifecycle/adapter/broker boundary tests | VALIDATED |
| Position persistence | SQLite store + LiveEngine cycle tests | VALIDATED at targeted-test level |
| Position recovery | runtime recovery + LiveEngine tests | VALIDATED at targeted-test level |
| Position reconciliation | runtime reconciliation + LiveEngine tests | VALIDATED at targeted-test level |
| Provider order capability | INDMoney order/positions APIs behind adapter | VALIDATED at contract level |
| Production live-order certification | Real-money runtime evidence | NOT CERTIFIED |
| Browser/UI certification | M0–M10 evidence incomplete | NOT CERTIFIED |
| Deployment certification | Post-deployment evidence incomplete | NOT CERTIFIED |

---

# 7. Known limitations / explicit dispositions

- REST full-quote timestamp semantics are not authoritative enough to treat every provider timestamp as live-price observation time; freshness/clock-skew state remains explicit.
- Intrinsic-value failures intentionally produce SUSPECT/DEGRADED integrity, not VALID.
- Provider `position_id` is not assumed to be canonical `client_order_id`; automatic broker-position reconciliation is not claimed until identity mapping is proven.
- No real-money order placement is executed by tests.
- Live execution remains uncertified until runtime evidence proves the complete decision → risk → intent → broker → result → reconciliation path.
- Production UI remains uncertified until browser/runtime evidence proves the canonical DashboardData projection is rendered without divergence.

---

# 8. Progress log

## Tracker initialization
**Status:** COMPLETE

Master tracker established as the persistent continuity source.

## R2-014 canonical analytics context
**Status:** COMPLETE

Canonical typed analytics context established while preserving compatibility projections.

## R2-015 execution foundation
**Status:** COMPLETE at targeted-contract level

Canonical intent/result, risk boundary, idempotency, lifecycle, paper/live boundaries, kill switch and runtime safety implemented and tested.

## R2-015 audit persistence/recovery
**Status:** COMPLETE at targeted-test level

Execution audit persistence, recovery decisions and runtime recovery wiring implemented and tested.

## R2-015 position state/recovery/reconciliation
**Status:** COMPLETE at targeted-test level

Canonical position state, lifecycle, persistence, recovery and reconciliation runtime boundaries implemented and tested.

## RuntimeContext canonical recovery fields
**Status:** IMPLEMENTED

`position_recovery` and `position_reconciliation` are now explicit shared runtime fields rather than relying on dynamic LiveEngine attributes.

Commit: `ec8251ac574ad026edd0b83f21ac227f92bf3847`

## M0 UI/backend audit
**Status:** IN PROGRESS

Inventory and gap analysis remains the active workstream. Backend capability does not constitute UI certification.

### M0 audit boundaries completed
- B1 — exact branch/HEAD confirmation: complete, tracker commit `af9ede4b021a7c8024208aec888b790df9e8ab60`.
- B2 — Streamlit/UI entry-point and legacy-path inventory: complete. Active canonical entry point `dashboard/app.py`; legacy `app/app.py` and `app/pages/*` remain classified as compatibility path; `app.services.LiveService` delegates to canonical `RuntimeManager` and does not own acquisition.
- B3 — UI adapter/presenter inventory: complete. Canonical adapters are `decision_adapter.py`, `intelligence_adapter.py`, `market_summary_adapter.py`, `provenance_adapter.py`, `ui_runtime_contract.py`, plus Decision ↔ Intelligence consistency mapping; legacy presentation remains explicitly separate.
- Next boundary: canonical `DashboardData` model and field inventory.

---

# 9. Per-change evidence contract

For every production behavior change, record:

1. Date/time
2. Milestone
3. Exact change
4. Files changed
5. Targeted tests + result
6. Full regression when applicable
7. Live evidence when applicable
8. Commit SHA
9. Checklist items completed
10. Remaining gaps
11. Exact next action

---

# 10. Completion rule

QuantNifty is complete only when M0–M11 are closed with evidence and the final production-readiness gate explicitly records certification.

Deployment alone never changes status to LIVE.

Any unresolved item must remain visible with a reason and disposition. Nothing is silently dropped.
