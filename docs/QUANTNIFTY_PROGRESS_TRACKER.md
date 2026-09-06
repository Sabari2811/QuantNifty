### M1 boundary B1 — Decision direction vs actionability audit
**Status: COMPLETE (audit-only; no behavior change)**

- `decision/models/decision.py` confirms the canonical Decision contains `signal`, `trade`, `market`, `reasons`, `score`, `strategy_name`, `authoritative_signal` and `validation`, but no independent `actionability` field.
- `decision/models/signal.py` contains only `name` and `confidence` for the signal object.
- `decision/decision_engine.py` treats `BUY CALL`, `BUY PUT` and `WAIT` as the valid decision directions; `DecisionBuilder` preserves an authoritative direction and computes confidence from score magnitude.
- `decision/models/execution_plan.py` already carries the executable trade-quality/risk/reward/entry/SL/target fields. `Trade` already carries contract/option/strike plus its execution plan.
- Therefore this audit does **not** invent or add an actionability field. Existing direction/signal and validation/execution-plan semantics remain unchanged. The earlier M0 “actionability” finding is reclassified here as **INTENTIONALLY UNAVAILABLE as a distinct current contract**, pending a future specification that defines actionability independently of direction/validation.
- Evidence files inspected: `decision/models/decision.py`, `decision/models/signal.py`, `decision/decision_engine.py`, `decision/decision_builder.py`, `decision/models/trade.py`, `decision/models/execution_plan.py`.
- Boundary date: 2026-09-06.
- Boundary commit: `7dab61399804f8a1b8ad5f03b133b0f48c792452`.

### M1 boundary B2 — Canonical execution/recovery projection
**Status: COMPLETE — targeted regression PASS**

- `models/dashboard_data.py` explicitly projects `execution_intent`, `execution_result`, `execution_lifecycle`, `position_recovery`, and `position_reconciliation` as canonical pass-through fields.
- `dashboard/dashboard_controller.py` maps those five fields directly from the same `RuntimeContext` cycle; no broker state is inferred and no execution semantics are recomputed.
- `dashboard/ui_runtime_contract.py` exposes those exact five objects to the real Streamlit runtime contract by direct pass-through.
- `tests/test_streamlit_runtime_ui_contract.py` creates deterministic `OrderIntent` / `ExecutionResult` and recovery/reconciliation fixtures and asserts identity preservation through the real Streamlit entrypoint contract.
- Static repository verification completed for all four modified files at commit `105464b6e0ea9b79b0d0e1e2a3325bd1043b8565`.
- GitHub Actions workflow runs for commit `105464b6e0ea9b79b0d0e1e2a3325bd1043b8565`: none available.
- Local targeted regression executed after synchronizing branch `r2-011-canonical-snapshot-provenance`: `pytest -q tests/test_streamlit_runtime_ui_contract.py` → **2 passed in 7.77s**.
- No provider credentials, broker calls, or real-money orders were required for this targeted test.

### M1 boundary B3 — Canonical option-chain quote projection (bid/ask)
**Status: COMPLETE — targeted regression PASS**

- `providers/indmoney_provider.py` already normalizes provider quote aliases into canonical `bid_price` / `ask_price`; this boundary closes the missing projection at `engine/option_chain_manager.py`.
- `engine/option_chain_manager.py` now carries `CE_BID`, `CE_ASK`, `PE_BID`, and `PE_ASK` directly from provider quote payloads without deriving them from LTP or other fields.
- Missing provider bid/ask values remain `None` / unknown; no synthetic spread or fallback value is introduced.
- `tests/test_option_chain_quote_fields.py` verifies both complete bid/ask preservation and missing bid/ask behavior using deterministic provider fixtures; no broker/provider network calls are performed.
- Implementation commit: `4660d61f35ff851afec6d61f6554a7d8d12473de`.
- Targeted regression commit: `31a9d899ae0fe941b42309a8ab4b62596c32de90`.
- Local targeted regression executed after synchronizing branch `r2-011-canonical-snapshot-provenance`: `pytest -q tests/test_option_chain_quote_fields.py` → **2 passed in 2.33s**.

### M1 boundary B4 — Canonical option-chain field contract (OI / volume / IV)
**Status: COMPLETE — targeted regression PASS**

- `engine/option_chain_manager.py` already projects raw provider `CE_OI` / `PE_OI` and `CE_VOLUME` / `PE_VOLUME` into the canonical option-chain dataframe.
- `analytics/oi/oi_flow_engine.py` derives `CE_OI_CHANGE` / `PE_OI_CHANGE` from current-vs-previous canonical snapshots; first-snapshot semantics remain explicitly awaiting a previous snapshot rather than fabricating a change.
- `engine/live_greeks_engine.py` derives `CE_IV` / `PE_IV` and the Greek fields through the canonical `GreeksEngine`; calculation failures remain missing rather than being replaced with synthetic values.
- `dashboard/components/option_chain.py` projects canonical Greek/analytics columns through `_merge_authoritative_greeks()` without recomputation or silent fallback.
- `tests/test_option_chain_canonical_field_contract.py` verifies preservation of bid/ask, OI, volume and IV through the Dashboard UI projection, and verifies that missing bid/ask remains missing rather than being invented.
- Implementation/test commit: `3bf3a1a1bc385bd7cba4083eddcc63b20b173448`.
- Local targeted regression executed after synchronizing branch `r2-011-canonical-snapshot-provenance`: `pytest -q tests/test_option_chain_canonical_field_contract.py` → **2 passed in 3.46s**.
- No provider credentials, broker calls, or real-money orders were required.

**Next action:** continue M1 field completeness with any remaining canonical option-chain/provenance contract gaps, then close M1 only after the required live option-chain UI certification evidence is established. Keep compatibility pages unchanged.

## M2 — UI/backend divergence elimination
**Status: NOT STARTED**

- [ ] Remove duplicate UI calculations
- [ ] Remove stale/duplicate adapters
- [ ] Fix field/type/enum mismatches
- [ ] Fix missing-value/fallback semantics
- [ ] Prevent fabricated values
- [ ] Preserve UNKNOWN / SUSPECT / INVALID
- [ ] Preserve freshness separately
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
