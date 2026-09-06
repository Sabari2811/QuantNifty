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
- No provider credentials, broker calls, or real-money orders were required.

### M1 boundary B3 — Canonical option-chain quote projection (bid/ask)
**Status: COMPLETE — targeted regression PASS**

- `engine/option_chain_manager.py` now carries `CE_BID`, `CE_ASK`, `PE_BID`, and `PE_ASK` directly from provider quote payloads without deriving them from LTP or other fields.
- Missing provider bid/ask values remain `None` / unknown; no synthetic spread or fallback value is introduced.
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
**Status: IN PROGRESS — B1+B2+B3+B4+B5 COMPLETE**

### M2 boundary B1 — KPI missing-value semantics
**Status: COMPLETE — targeted regression PASS**

- `dashboard/components/kpi_cards.py` no longer defaults missing `bullish_probability` or `confidence` to `0`; missing/NaN values render as `—`.
- A real zero remains `0%`; known numeric percentages remain unchanged.
- Regression coverage: `tests/test_dashboard_kpi_contract.py`.
- Implementation commit: `4353fab943d100bf08f28ebbc01f6145e97a2b45`.
- Test coverage commit: `1e55baa2b66445677298786b6eb7fb32cc91ada7`.
- Local targeted regression: `pytest -q tests/test_dashboard_kpi_contract.py` → **3 passed in 2.30s**.

### M2 boundary B2 — Expected-move / Max-Pain / PCR missing-value semantics
**Status: COMPLETE — targeted regression PASS**

- `dashboard/components/expected_move_card.py` safely reads canonical keys and renders `UNAVAILABLE` for missing/non-numeric/NaN/infinite values.
- `dashboard/components/max_pain_card.py` renders missing/invalid values as `UNAVAILABLE`, while preserving real zero values.
- `dashboard/components/pcr_card.py` renders missing/invalid PCR and sentiment as `UNAVAILABLE`.
- Regression coverage: `tests/test_expected_move_card_contract.py`, `tests/test_max_pain_card_contract.py`, `tests/test_pcr_card_contract.py`.
- Implementation commits: `7f99e94632e40c68f9e3d7f273ad937a4b4c5e9e`, `4c37f78ce10be79bf284528c7baa306012119b8a`, `b4a54f6b12d60706fe8d58ae9a5c99b8ab123d29`.
- Local targeted regression: `pytest -q tests/test_expected_move_card_contract.py tests/test_max_pain_card_contract.py tests/test_pcr_card_contract.py` → **7 passed in 2.68s**.

### M2 boundary B3 — Probability gauge missing-value semantics
**Status: COMPLETE — targeted regression PASS**

- `dashboard/components/probability_gauge.py` now normalizes missing, non-numeric, NaN and infinite probability to an unavailable value while preserving valid numeric values including zero.
- Regression coverage: `tests/test_probability_gauge_contract.py`.
- Implementation commit: `0409f27dffd493ca8218329bf83d575bf238e8d7`.
- Regression test file commit: `823db1c0ae9c6700dfc511830044f4718b584088`.
- Local targeted regression: `pytest -q tests/test_probability_gauge_contract.py` → **3 passed in 1.32s**.

### M2 boundary B4 — Market-banner missing/invalid presentation semantics
**Status: COMPLETE — targeted regression PASS**

- `dashboard/components/market_banner.py` now fails closed for missing/invalid Spot, Gamma Flip/Wall, probability, confidence, recommendation and risk/reward presentation values.
- Real zero values are preserved rather than interpreted as missing.
- Regression coverage: `tests/test_market_banner_contract.py`.
- Implementation commit: `2ea2dbbb2a4b6ced8fb008b6559fc3f4c646fab5`.
- Local targeted regression: `pytest -q tests/test_market_banner_contract.py` → **2 passed in 2.51s**.

### M2 boundary B5 — Signal-card missing/invalid presentation semantics
**Status: COMPLETE — targeted regression PASS**

- `dashboard/components/signal_card.py` now renders missing/invalid dealer presentation values explicitly as `UNAVAILABLE` instead of leaking raw `None`/invalid values into the UI.
- Canonical decision direction, probability and confidence remain presentation-only; no signal recomputation or actionability inference is introduced.
- Regression coverage: `tests/test_signal_card_contract.py`.
- Implementation commit: `75db714ceb74c0397997bc241c3e54acab2fd270`.
- Regression test file commit: `70895444889fee09b4b3ca1845458038fa7d5838`.
- Local targeted regression: `pytest -q tests/test_signal_card_contract.py` → **3 passed in 1.44s**.
- No provider credentials, broker calls, or real-money orders were required.

- [ ] Remove duplicate UI calculations
- [ ] Remove stale/duplicate adapters
- [ ] Fix field/type/enum mismatches
- [x] Fix missing-value/fallback semantics
- [x] Prevent fabricated values
- [ ] Preserve UNKNOWN / SUSPECT / INVALID
- [ ] Preserve freshness separately
- [ ] Preserve direction/actionability separation
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
