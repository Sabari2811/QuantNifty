# QuantNifty Progress Tracker

## M1 — Canonical dashboard/runtime boundary

### M1 boundary B1 — Decision direction vs actionability audit
**Status: COMPLETE (audit-only; no behavior change)**

- `decision/models/decision.py` confirms the canonical Decision contains `signal`, `trade`, `market`, `reasons`, `score`, `strategy_name`, `authoritative_signal` and `validation`, but no independent `actionability` field.
- `decision/models/signal.py` contains only `name` and `confidence` for the signal object.
- `decision/decision_engine.py` treats `BUY CALL`, `BUY PUT` and `WAIT` as the valid decision directions; `DecisionBuilder` preserves an authoritative direction and computes confidence from score magnitude.
- `decision/models/execution_plan.py` already carries the executable trade-quality/risk/reward/entry/SL/target fields. `Trade` already carries contract/option/strike plus its execution plan.
- Therefore this audit does **not** invent or add an actionability field. Existing direction/signal and validation/execution-plan semantics remain unchanged. The earlier M0 “actionability” finding is reclassified here as **INTENTIONALLY UNAVAILABLE as a distinct current contract**, pending a future specification that defines actionability independently of direction/validation.
- Boundary date: 2026-09-06.
- Boundary commit: `7dab61399804f8a1b8ad5f03b133b0f48c792452`.

### M1 boundary B2 — Canonical execution/recovery projection
**Status: COMPLETE — targeted regression PASS**

- `models/dashboard_data.py` explicitly projects `execution_intent`, `execution_result`, `execution_lifecycle`, `position_recovery`, and `position_reconciliation` as canonical pass-through fields.
- `dashboard/dashboard_controller.py` maps those five fields directly from the same `RuntimeContext` cycle; no broker state is inferred and no execution semantics are recomputed.
- `dashboard/ui_runtime_contract.py` exposes those exact five objects to the real Streamlit runtime contract by direct pass-through.
- `tests/test_streamlit_runtime_ui_contract.py` creates deterministic execution/recovery/reconciliation fixtures and asserts identity preservation through the real Streamlit entrypoint contract.
- Implementation commit: `105464b6e0ea9b79b0d0e1e2a3325bd1043b8565`.
- Local targeted regression: `pytest -q tests/test_streamlit_runtime_ui_contract.py` → **2 passed in 7.77s**.

### M1 boundary B3 — Canonical option-chain quote projection (bid/ask)
**Status: COMPLETE — targeted regression PASS**

- `engine/option_chain_manager.py` carries `CE_BID`, `CE_ASK`, `PE_BID`, and `PE_ASK` directly from provider quote payloads without deriving them from LTP or other fields.
- Missing provider bid/ask values remain unknown; no synthetic spread or fallback value is introduced.
- Regression coverage: `tests/test_option_chain_quote_fields.py`.
- Implementation commit: `4660d61f35ff851afec6d61f6554a7d8d12473de`.
- Targeted regression commit: `31a9d899ae0fe941b42309a8ab4b62596c32de90`.
- Local targeted regression: `pytest -q tests/test_option_chain_quote_fields.py` → **2 passed in 2.33s**.

### M1 boundary B4 — Canonical option-chain field contract (OI / volume / IV)
**Status: COMPLETE — targeted regression PASS**

- `engine/option_chain_manager.py` projects raw provider OI/volume into the canonical option-chain dataframe.
- `analytics/oi/oi_flow_engine.py` derives OI change from current-vs-previous canonical snapshots; first-snapshot semantics remain explicitly awaiting a previous snapshot.
- `engine/live_greeks_engine.py` derives `CE_IV` / `PE_IV` and Greek fields through the canonical Greeks engine; calculation failures remain missing.
- `dashboard/components/option_chain.py` projects canonical Greek/analytics columns without recomputation or silent fallback.
- Regression coverage: `tests/test_option_chain_canonical_field_contract.py`.
- Implementation/test commit: `3bf3a1a1bc385bd7cba4083eddcc63b20b173448`.
- Local targeted regression: `pytest -q tests/test_option_chain_canonical_field_contract.py` → **2 passed in 3.46s**.

**M1 implementation status:** implementation/test boundaries B1–B4 are complete. Final M1 live UI certification remains evidence-gated.

## M2 — UI/backend divergence elimination
**Status: IN PROGRESS — B1+B2+B3+B4+B5+B6+B7 COMPLETE**

### M2 boundary B1 — KPI missing-value semantics
**Status: COMPLETE — targeted regression PASS**

- `dashboard/components/kpi_cards.py` renders missing/NaN `bullish_probability`/`confidence` as `—`; real zero remains `0%`.
- Regression coverage: `tests/test_dashboard_kpi_contract.py` → **3 passed in 2.30s**.

### M2 boundary B2 — Expected-move / Max-Pain / PCR missing-value semantics
**Status: COMPLETE — targeted regression PASS**

- Expected Move, Max Pain, PCR and sentiment now fail closed to `UNAVAILABLE` for missing/non-numeric/NaN/infinite values while preserving valid zero values.
- Regression coverage: `tests/test_expected_move_card_contract.py`, `tests/test_max_pain_card_contract.py`, `tests/test_pcr_card_contract.py` → **7 passed in 2.68s**.

### M2 boundary B3 — Probability gauge missing-value semantics
**Status: COMPLETE — targeted regression PASS**

- Missing/non-numeric/NaN/infinite probability is unavailable; valid zero remains zero.
- Regression coverage: `tests/test_probability_gauge_contract.py` → **3 passed in 1.32s**.

### M2 boundary B4 — Market-banner missing/invalid presentation semantics
**Status: COMPLETE — targeted regression PASS**

- Spot, Gamma Flip/Wall, probability, confidence, recommendation and risk/reward now fail closed when unavailable/invalid; valid zero is preserved.
- Regression coverage: `tests/test_market_banner_contract.py` → **2 passed in 2.51s**.

### M2 boundary B5 — Signal-card missing/invalid presentation semantics
**Status: COMPLETE — targeted regression PASS**

- Missing/invalid dealer presentation values are explicitly `UNAVAILABLE`; no signal recomputation or actionability inference is introduced.
- Regression coverage: `tests/test_signal_card_contract.py` → **3 passed in 1.44s**.

### M2 boundary B6 — Provenance unavailable-state preservation
**Status: COMPLETE — targeted regression PASS**

- Missing runtime provenance remains explicit `UNAVAILABLE`; coverage, integrity and freshness stay separate.
- Option-chain quality is `READY` only for complete/VALID, `DEGRADED` for incomplete/SUSPECT/INVALID, and `UNAVAILABLE` when required statuses are absent.
- Regression coverage: `tests/test_provenance_adapter_contract.py` → **3 passed in 0.29s**.

### M2 boundary B7 — Runtime card contract
**Status: COMPLETE — regression added; CI certification pending**

- `dashboard/components/runtime_card.py` is presentation-only and renders runtime/cycle/trade/block/open-position/last-trade state from canonical dashboard data.
- Missing/non-finite values fail closed to `UNAVAILABLE`; valid zero/false values are preserved.
- Status icons are deterministic and unknown statuses remain neutral.
- Regression coverage: `tests/test_runtime_card_contract.py`.

### M2 remaining audit boundaries
- [ ] Remove duplicate UI calculations
- [ ] Remove stale/duplicate adapters
- [x] Fix field/type/enum mismatches
- [x] Fix missing-value/fallback semantics
- [x] Prevent fabricated values
- [x] Preserve UNKNOWN / SUSPECT / INVALID
- [x] Preserve freshness separately
- [x] Preserve direction/actionability separation
- [ ] Prevent history/replay vetoes
- [x] Regression coverage for every correction

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

## M6 — Execution safety and lifecycle
**Status: IN PROGRESS**

- [x] Runtime execution gate
- [x] Risk validation gate
- [x] Canonical execution intent/result
- [x] Broker UNKNOWN on timeout/connection failure
- [x] Execution lifecycle classification
- [ ] Full deterministic regression certification
- [ ] Live broker certification

## M7 — Reconciliation and position lifecycle
**Status: IN PROGRESS**

- [x] Reconciliation lifecycle exists
- [x] UNKNOWN cannot be retried before reconciliation
- [x] Position open/close/stop/target lifecycle exists
- [x] Recovery projection exists
- [x] Explicit MATCH/MISMATCH continuation gate
- [ ] Full regression certification
- [ ] Broker-state certification

## M8 — Runtime recovery / operational safety
**Status: IN PROGRESS**

- [x] Runtime singleton recovery hardened against partial initialization
- [x] Local instrument-master operations do not require broker credentials
- [x] Credential requirement retained for provider downloads
- [ ] End-to-end recovery rehearsal
- [ ] Restart/recovery certification

## M9 — Streamlit runtime certification
**Status: IN PROGRESS**

- [x] Canonical dashboard controller cycle
- [x] Runtime UI contract
- [x] Runtime card
- [x] Canonical option-chain presentation
- [ ] Full Streamlit AppTest regression
- [ ] Degraded/live-state UI certification

## M10 — CI / regression certification
**Status: IN PROGRESS**

- [x] Python 3.12 CI environment
- [x] Dependency installation
- [x] Compile gate
- [x] Regression workflow
- [ ] Full suite green on current `main`
- [ ] Release regression rerun after all changes

## M11 — Deployment / live validation
**Status: IN PROGRESS — evidence gated**

- [x] Dedicated Render validation service for `Sabari2811/QuantNifty/main`
- [x] Render deployment reached LIVE on validated prior commit
- [ ] Redeploy current `main` after regression gate is green
- [ ] Streamlit runtime smoke validation
- [ ] Live APITOKEN validation when configured in the dedicated validation service
- [ ] Final coverage/freshness/integrity/decision/execution/recovery certification
- [ ] No-real-money-order certification

**Global safety rule:** deployment is not certification. Live execution remains blocked unless all canonical runtime, data-quality, decision, risk, reconciliation and execution gates pass. UNKNOWN broker outcomes require reconciliation before retry. No real-money orders are used for automated regression validation.
