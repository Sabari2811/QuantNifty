# QuantNifty — Master Project Tracker, Summary & Architecture

## 1. Project summary

QuantNifty is a modular NIFTY options analytics, decision-intelligence, paper/live-execution and certification platform.

**Current objective:** move from validated live analytics into a fully auditable, risk-controlled production system without bypassing canonical backend contracts.

**Current branch:** `r2-011-canonical-snapshot-provenance`  
**Current phase:** M1 — Canonical Dashboard contract  
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
**Status: COMPLETE**

- [x] Confirm exact branch/HEAD
- [x] Inventory all Streamlit/UI entry points
- [x] Inventory UI components/pages
- [x] Inventory UI adapters/presenters
- [x] Inventory canonical DashboardData models
- [x] Inventory backend-produced fields
- [x] Inventory every UI-rendered field
- [x] Map provider → canonical backend → DashboardData → adapter → UI
- [x] Identify UI-side calculations/recomputation
- [x] Identify hardcoded/default/fallback values
- [x] Identify stale/legacy UI paths
- [x] Identify missing backend fields
- [x] Identify unused backend capabilities
- [x] Create complete UI/backend gap matrix
- [x] Assign every item VALIDATED / FIX REQUIRED / INTENTIONALLY UNAVAILABLE / UNSUPPORTED
- [x] Record audit evidence and commit SHA

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
Boundary commit: `f6bc7b53c23530f925c21811d364d56f856aea80`.

### M0 boundary B4 — Canonical DashboardData model and field inventory
**Status: COMPLETE**

- `models/dashboard_data.py` defines the canonical DashboardData projection used by `dashboard/dashboard_controller.py` and the active Streamlit dashboard.
- Core identity/data fields: `provider`, `symbol`, `spot`, `expiry`, `option_chain`, `greeks`.
- Canonical analytics fields: `dealer`, `dealer_flow`, `expected_move`, `max_pain`, `pcr`, `market_structure`, `liquidity`, `probability`, `signal`, `trade_plan`, `risk`, `institutional_score`.
- Provenance/quality fields: `data_provenance`, `option_chain_integrity`.
- Intelligence fields: adapted `intelligence`, canonical `canonical_intelligence`, and `decision_intelligence_consistency`.
- Runtime/operational fields: `portfolio`, `position`, `last_trade`, `journal`, `statistics`, `risk_state`, `trade_status`, `trade_block_reason`, `runtime_status`, `cycle_no`.
- `analytics` is explicitly retained as the generic serialized/backward-compatible display projection; dedicated DashboardData fields are mapped from typed `RuntimeContext.market_context` by `DashboardController` and are not sourced from conflicting generic analytics.
- `MarketContext` remains the internal typed canonical analytics model and includes additional fields (`gamma_flip`, `gamma_wall`, `oi_flow`, `iv_skew`, `iv_smile`, `atr`, `volatility`, `technical`, `oi_shift`, `smart_strike`, `market_map`) that are not all exposed as dedicated DashboardData fields; these require downstream disposition rather than assumptions.
- Evidence files inspected: `models/dashboard_data.py`, `models/market_context.py`, `models/dealer_data.py`, `dashboard/dashboard_controller.py`, `dashboard/components/*` consumers already traced above.
- Boundary date: 2026-09-06.
- Boundary commit: `79cb6ecdaa42928eb2eeef61aa42fea99cf9404e`.

### M0 boundary B5 — Backend-produced canonical analytics inventory
**Status: COMPLETE**

- `analytics/analytics_pipeline.py` explicitly instantiates and runs the canonical analytics engines for gamma, dealer/dealer-flow, delta/vanna/charm, liquidity, OI flow, IV skew/smile, expected move, Max Pain, PCR, ATR/volatility, market structure, technicals, probability, signal, institutional score, smart strike, trade plan, risk and market map.
- The pipeline constructs a typed `MarketContext`, assigns the canonical analytics fields, and returns those analytics in the established dictionary projection alongside `context` and `greeks`.
- `core/runtime_context.py` promotes the typed `MarketContext` into `RuntimeContext.market_context`; `RuntimeContext.analytics` remains the serialized/backward-compatible projection.
- Backend-produced canonical analytics fields are therefore evidenced as: `dealer`, `dealer_flow`, `liquidity`, `gamma_flip`, `gamma_wall`, `oi_flow`, `iv_skew`, `iv_smile`, `expected_move`, `max_pain`, `pcr`, `market_structure`, `atr`, `volatility`, `technical`, `probability`, `signal`, `smart_strike`, `trade_plan`, `risk`, `institutional_score`, `market_map`, plus `greeks` and the raw market identity values carried by runtime context.
- No backend calculation was changed in this boundary; this is inventory/reconciliation only.
- Evidence files inspected: `analytics/analytics_pipeline.py`, `core/runtime_context.py`, `models/market_context.py`, `models/dashboard_data.py`.
- Boundary date: 2026-09-06.
- Boundary commit: `57406a594146030513e23cc6c8372df16159e534`.

### M0 boundary B6 — UI-rendered field inventory and legacy-field classification
**Status: COMPLETE**

Canonical `dashboard/*` rendering is evidenced across the active Streamlit entrypoint:
- Header: symbol, spot, expiry, provider/session, latest acquisition time derived from runtime provenance.
- Market banner/signal: decision signal, bullish probability, confidence, dealer gamma/market mode, gamma flip/wall, recommendation and risk/reward.
- Market regime: dealer gamma/mode, expected volatility, confidence, bullish/bearish probability, mean reversion, breakout, gamma flip/wall and total GEX.
- Intelligence: direction, conviction, opportunity, recommendation, regime, data coverage, freshness, integrity, scenarios, explanation and Decision ↔ Intelligence consistency.
- Market summary: spot/expiry/expected-move values through `adapt_market_summary()`; no UI recomputation.
- Analytics cards: institutional score, probability, Max Pain, PCR, market structure, dealer flow, liquidity, trade plan and risk.
- Option chain/Greeks: same-cycle option chain and Greeks, with coverage/freshness/integrity and explicit degraded state via `provenance_adapter`/option-chain renderer.
- Charts: same-cycle Greeks/MarketContext-backed dashboard values.
- Generic analytics expander: `DashboardData.analytics` is displayed as an explicit compatibility/audit surface, not used as the dedicated-field source.

Legacy `app/*` rendering is a separate compatibility surface and exposes fields that are not all first-class DashboardData fields, including:
- portfolio cash/invested/realized/unrealized P&L and trade-quality summaries;
- direct `ctx.snapshot` / `ctx.decision` presentation;
- technical EMA/VWAP checklist state and PCR bias;
- market-map dealer/gamma/max-pain/expected-move summaries;
- active position entry/current/quantity/SL/target/holding/MTM;
- execution-plan strike/option/premium stop/targets/risk-reward/quality/lots;
- legacy live option-chain annotations derived from `ctx.analytics`.

Legacy components also contain explicit display defaults such as `"-"`, `"--"`, `0`, and a dynamic holding-time calculation. These are recorded as compatibility-path audit findings and are not silently promoted to canonical DashboardData semantics.

Evidence files inspected: `dashboard/components/*` canonical renderers; `app/components/hero_header.py`, `kpi_cards.py`, `ai_decision_card.py`, `market_intelligence_card.py`, `active_position_card.py`, `checklist_panel.py`, `market_map_panel.py`, `trade_plan_card.py`, `live_option_chain.py`.
Boundary date: 2026-09-06.
Boundary commit: `3cc34c22f2b062988317cb3389d356b92063a37e`.

### M0 boundary B7 — Provider → canonical backend → DashboardData → adapter → UI field-family trace
**Status: COMPLETE**

- Provider identity/source: `providers/indmoney_provider.py` supplies normalized spot/option/historical quote data and preserves provider timestamps; market-data normalization does not synthesize market values.
- Live market-data provenance: `engine/market_data_pipeline.py` populates `RuntimeContext.data_provenance` for spot, option-chain and candles, including coverage, freshness, timestamp and integrity state; option-chain integrity is attached to the same-cycle dataframe/context.
- Canonical analytics: `engine/live_engine.py` runs `MarketDataPipeline`, verifies option-chain readiness, runs `AnalyticsPipeline`, promotes `MarketContext`, creates the canonical `MarketSnapshot`, builds Decision/Intelligence and carries the runtime state forward.
- Dashboard projection: `dashboard/dashboard_controller.py` maps `RuntimeContext.market_context` and other same-cycle runtime artifacts to typed `DashboardData`.
- UI adapter/presenter: `dashboard/decision_adapter.py`, `market_summary_adapter.py`, `intelligence_adapter.py`, `provenance_adapter.py` and the component presenters consume the DashboardData projection; `option_chain.render()` receives same-cycle option chain, Greeks, provenance and integrity.
- Evidence for field dispositions: `tests/test_dashboard_canonical_field_disposition.py` proves all typed canonical analytics fields have exactly one disposition: dedicated DashboardData, existing canonical mapping, or generic analytics-only compatibility surface. `tests/test_market_data_pipeline_provenance.py` proves provider timestamps/freshness/integrity survive into runtime provenance.
- No runtime behavior was changed in this boundary; this is a field-family trace and evidence classification only.
- Boundary date: 2026-09-06.
- Boundary commit: `0636409f82e1d7803ec61d8bf5f5322ec685eafe`.

### M0 boundary B8 — UI-side recomputation / fallback audit
**Status: COMPLETE (findings recorded; no behavior change)**

- Canonical dashboard renderers inspected for calculation ownership. Presentation-time formatting, sorting, styling and chart construction do not recompute the canonical analytics values.
- Canonical option-chain renderer delegates provenance state to `provenance_adapter` and renders same-cycle values; no alternate market-data calculation path was introduced.
- Canonical dashboard adapters are projection-only except for explicit semantic presentation states such as READY/DEGRADED/UNAVAILABLE and display formatting.
- Legacy compatibility UI contains UI-side derived presentation logic, including OI-history status/count aggregation in `app/pages/option_chain.py`, dynamic holding-time in `app/components/active_position_card.py`, and dealer/market interpretation text in `app/components/market_map_panel.py`.
- Legacy compatibility UI also contains hardcoded/default fallbacks for missing values, including `0`, `"-"`, `"--"`, and default runtime/replay states. These are not authoritative canonical values.
- The canonical `OIFlowEngine` explicitly distinguishes `UNKNOWN`, `NO_CHANGE`, and `AWAITING_PREVIOUS_SNAPSHOT`; therefore legacy zero-default flow counts must not be treated as canonical “no flow”. This is a genuine compatibility-path semantic gap and is deferred to M2 rather than altered during M0.
- Evidence files inspected: canonical renderers/adapters plus `app/pages/option_chain.py`, `app/pages/runtime.py`, `app/pages/replay.py`, `app/components/active_position_card.py`, `app/components/market_map_panel.py`, `analytics/oi/oi_flow_engine.py`.
- Boundary date: 2026-09-06.
- Boundary commit: `c12d64b201d27c2c03d853dfa8c599ea523f6b19`.

### M0 boundary B9 — Final M0 gap matrix and disposition classification
**Status: COMPLETE**

| Gap / field family | Evidence | Disposition | Downstream milestone |
|---|---|---|---|
| Spot / expiry / option chain / Greeks | `MarketDataPipeline` → `RuntimeContext` → `DashboardController` → canonical components | VALIDATED | M1/M3 |
| Dealer / dealer flow / GEX / gamma levels | `MarketContext` + `DealerData` → `DashboardData` → canonical cards | VALIDATED | M1/M4 |
| Expected Move / Max Pain / PCR | canonical adapters + cards | VALIDATED | M1/M4 |
| Market structure / liquidity / probability / signal / trade plan / risk / institutional score | `DashboardController` + dedicated components | VALIDATED | M1/M4 |
| Intelligence / consistency / freshness / integrity / provenance | typed `IntelligenceResult` + `provenance_adapter` + runtime contract | VALIDATED | M1/M4/M5 |
| Gamma flip / gamma wall | canonical `DealerData` fields and existing renderer mapping | VALIDATED | M1/M4 |
| Smart strike | included in canonical backend surface and represented by trade-plan path; no standalone DashboardData field | VALIDATED (represented by existing mapping) | M1/M4 |
| OI flow / IV skew / IV smile / ATR / volatility / technical / OI shift / market map | typed `MarketContext`, retained in generic `DashboardData.analytics`; no dedicated canonical UI field | INTENTIONALLY UNAVAILABLE as dedicated DashboardData UI; compatibility-only access remains explicit | M1/M4 |
| Execution intent / execution result / execution lifecycle | present on `RuntimeContext`, absent from `DashboardData` and active canonical UI projection | FIX REQUIRED | M6 |
| Position recovery / position reconciliation | present on `RuntimeContext`, absent from `DashboardData` and active canonical UI projection | FIX REQUIRED | M7 |
| Decision actionability | direction exists in canonical decision engine; no distinct actionability field was found | FIX REQUIRED | M1/M4/M6 |
| Legacy OI-history UI derivation and zero-default flow counters | `app/pages/option_chain.py` vs canonical `OIFlowEngine` states | FIX REQUIRED | M2 |
| Legacy runtime/replay placeholder controls and stale “Coming Soon” surfaces | `app/pages/runtime.py`, `app/pages/replay.py` | FIX REQUIRED | M2/M9 |
| Legacy default/fallback presentation (`0`, `-`, `--`, READY) | reachable `app/*` compatibility components | FIX REQUIRED where semantics can misrepresent missing/unknown state | M2/M9 |
| Canonical generic analytics expander | `dashboard/app.py` explicitly renders `DashboardData.analytics` | VALIDATED as compatibility/audit surface | M1/M9 |
| Provider timestamp / freshness / integrity propagation | `INDMoneyProvider` + `MarketDataPipeline` + provenance tests | VALIDATED | M3/M5 |

Audit conclusion: there is no unexplained canonical market-data/analytics rendering path remaining within the audited surface. The remaining gaps are explicit contract/UI omissions or reachable legacy compatibility findings and are assigned to downstream milestones rather than hidden or treated as complete.

Evidence files/tests inspected: `dashboard/app.py`, `dashboard/dashboard_controller.py`, `models/dashboard_data.py`, `models/market_context.py`, `core/runtime_context.py`, `analytics/analytics_pipeline.py`, `decision/decision_engine.py`, `decision/decision_builder.py`, `analytics/oi/oi_flow_engine.py`, `providers/indmoney_provider.py`, `engine/market_data_pipeline.py`, `tests/test_dashboard_canonical_field_disposition.py`, `tests/test_market_data_pipeline_provenance.py`, `tests/test_streamlit_runtime_ui_contract.py`, plus audited canonical/legacy UI components.
Boundary date: 2026-09-06.
Boundary commit: `14f8778651406ba681523c3572c742fd15412bad`.

### M0 evidence closure — FINAL
**Status: COMPLETE**

- All M0 checklist items are explicitly dispositioned.
- All discovered canonical/legacy UI surfaces and fields are represented in the final gap matrix.
- All remaining gaps have explicit downstream ownership and are not hidden.
- No real-money execution was run.
- No provider credentials or user-side secret action is required to close M0.
- M0 completion date: 2026-09-06.
- Final M0 evidence closure commit: recorded by this tracker update.

**Next action:** start M1 from the first FIX REQUIRED canonical contract gap: introduce a distinct actionability contract only after inspecting the existing decision/intelligence models and their tests. Do not modify legacy compatibility pages as part of the first M1 change.

**M0 exit gate:** PASSED — every audited surface/field has an evidence-backed disposition.

## M1 — Canonical Dashboard contract
**Status: IN PROGRESS**

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
**Status: NOT STARTED

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
**Status: NOT STARTED

- [ ] All analytics fields and semantics
- [ ] Direction/actionability/decision
- [ ] Intelligence explanation
- [ ] Gamma flip semantics
- [ ] IV skew heuristic semantics
- [ ] WAIT behavior
- [ ] Historical/replay isolation

## M5 — Provenance/data-quality UI
**Status: NOT STARTED

- [ ] Source/provider
- [ ] Observation/processing timestamps
- [ ] Freshness/freshness reason
- [ ] Coverage/missing count
- [ ] Integrity/integrity reason
- [ ] Degraded/provider-failure/partial states
- [ ] Clock skew/structural invalidity
- [ ] SUSPECT/INVALID representation

## M6 — Decision → execution UI
**Status: NOT STARTED

- [ ] Intent/client ID
- [ ] Instrument/action/quantity/price
- [ ] Risk decision/block reason
- [ ] Kill-switch state
- [ ] Execution status/broker ID/fills
- [ ] Retry/reconciliation state
- [ ] Paper/live mode
- [ ] No accidental live-order control

## M7 — Position/recovery UI
**Status: NOT STARTED

- [ ] Position state/lifecycle
- [ ] Entry/current/SL/target/trailing
- [ ] Client/broker identities
- [ ] Persisted state
- [ ] Recovery/reconciliation
- [ ] Manual-resolution requirement
- [ ] Restart block
- [ ] No inferred broker position

## M8 — Failure/degraded-state UI certification
**Status: NOT STARTED

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
**Status: NOT STARTED

- [ ] DashboardData → adapter
- [ ] Adapter → UI
- [ ] Field completeness
- [ ] No recomputation
- [ ] Provenance/freshness/integrity
- [ ] Degraded states
- [ ] Decision/execution/position/recovery states
- [ ] Full regression

## M10 — End-to-end certification
**Status: NOT STARTED

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
**Status: NOT STARTED

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
| Spot | RuntimeContext / MarketDataPipeline | DashboardController | header/market summary | VALIDATED | B7/B9 |
| Expiry | RuntimeContext / instrument resolution | DashboardController / market summary adapter | header/market summary | VALIDATED | B7/B9 |
| Option chain | RuntimeContext / MarketDataPipeline | DashboardController | option_chain / OI heatmap | VALIDATED | B7/B9 |
| Greeks | LiveEngine / AnalyticsPipeline | DashboardController | greeks table / charts / heatmaps | VALIDATED | B7/B9 |
| GEX / DEX | MarketContext dealer/dealer_flow + Greeks | DashboardController | dealer / flow / charts | VALIDATED | B7/B9 |
| Gamma walls / flip | MarketContext + DealerData | DashboardController | dealer / banner / option-chain annotations | VALIDATED | B6/B9 |
| Expected Move / Max Pain / PCR | MarketContext | market_summary_adapter + cards | canonical cards | VALIDATED | B7/B9 |
| IV skew / dealer flow | IV skew typed in MarketContext; dealer_flow dedicated | no dedicated skew adapter; dealer_flow direct | dealer flow card; skew compatibility-only | INTENTIONALLY UNAVAILABLE for dedicated skew UI | B5/B9 |
| Market structure | MarketContext | DashboardController | market_structure card | VALIDATED | B6/B9 |
| Direction / actionability | DecisionEngine / DecisionBuilder | decision_adapter | signal/banner/intelligence; actionability absent | FIX REQUIRED for distinct actionability field | B9 |
| Decision / intelligence | DecisionEngine / Intelligence | decision/intelligence adapters | signal/intelligence cards | VALIDATED except actionability gap | B9 |
| Provenance / freshness / integrity | RuntimeDataProvenance / option-chain integrity | provenance_adapter | header/option-chain/intelligence/runtime | VALIDATED | B7/B9 |
| Execution | RuntimeContext execution state | no canonical DashboardData adapter | no active canonical execution UI | FIX REQUIRED | B9 |
| Position / recovery / reconciliation | RuntimeContext position state | no canonical DashboardData adapter | position fields partly present; recovery/reconciliation absent | FIX REQUIRED | B9 |

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
- The legacy `app/*` Streamlit path remains a reachable compatibility surface. Its explicit UI-side calculations/fallbacks and stale placeholder controls are known findings assigned to M2/M9; they are not treated as canonical data paths.
- `DecisionEngine` / `DecisionBuilder` currently expose direction/signal and confidence but no distinct actionability contract; this remains a deliberate FIX REQUIRED gap for M1/M4/M6 rather than an inferred equivalence.
- `RuntimeContext` carries execution intent/result/lifecycle and position recovery/reconciliation, but `DashboardData` does not currently project those fields; this remains a FIX REQUIRED gap for M6/M7.

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
**Status:** COMPLETE

M0 inventory, field tracing, calculation/fallback audit and disposition matrix are closed with evidence. No canonical runtime behavior was changed during M0.

### M0 audit boundaries completed
- B1 — exact branch/HEAD confirmation: complete, tracker commit `af9ede4b021a7c8024208aec888b790df9e8ab60`.
- B2 — Streamlit/UI entry-point and legacy-path inventory: complete. Active canonical entry point `dashboard/app.py`; legacy `app/app.py` and `app/pages/*` remain classified as compatibility path; `app.services.LiveService` delegates to canonical `RuntimeManager` and does not own acquisition.
- B3 — UI adapter/presenter inventory: complete. Canonical adapters are `decision_adapter.py`, `intelligence_adapter.py`, `market_summary_adapter.py`, `provenance_adapter.py`, `ui_runtime_contract.py`, plus Decision ↔ Intelligence consistency mapping; legacy presentation remains explicitly separate.
- B4 — canonical DashboardData model and field inventory: complete. Dedicated UI fields are typed in `DashboardData`; generic `analytics` is retained only as compatibility/display projection; additional typed MarketContext fields receive explicit dispositions.
- B5 — backend-produced canonical analytics inventory: complete. `AnalyticsPipeline` and `RuntimeContext` expose the canonical analytics surface without calculation changes; typed fields and compatibility projection are explicitly distinguished.
- B6 — UI-rendered field inventory and legacy-field classification: complete. Canonical dashboard rendering is traced across identity, decision, intelligence, analytics, option-chain/Greeks, provenance and runtime fields; legacy UI fields/defaults are recorded as compatibility-path findings.
- B7 — provider → canonical backend → DashboardData → adapter → UI field-family trace: complete. Provider normalization, runtime provenance, canonical analytics, DashboardData projection and UI adapter/presenter consumption are evidenced; no behavior changed in this boundary.
- B8 — UI-side recomputation / fallback audit: complete. Canonical dashboard rendering remains projection/presentation-only; legacy compatibility paths contain explicit derived display logic and fallback semantics, including OI-flow zero defaults that conflict with canonical UNKNOWN/NO_CHANGE distinctions. These findings are deferred to M2 unless they are required to close a certified canonical UI path.
- B9 — final M0 gap matrix and disposition classification: complete. All audited field families and reachable UI findings are classified as VALIDATED, FIX REQUIRED, INTENTIONALLY UNAVAILABLE, or UNSUPPORTED with downstream milestone ownership. Remaining action was final evidence closure.
- M0 evidence closure — final: complete. All checklist items are now checked, the gap matrix is recorded, and the M0 exit gate passed.
- Next active milestone: M1 — Canonical Dashboard contract.

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
