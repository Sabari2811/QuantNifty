# QuantNifty Project Continuation State

## Current Status
- Branch: `r2-011-canonical-snapshot-provenance`
- R2-013: closed/green with explicit live integrity caveat.
- R2-014 Slices 1–6: implemented and validated.
- Current R2-014 release gate: **OPEN** pending downstream canonical-consumer audit.

## R2-014 Slice 6
Intelligence canonical input boundary is green.
- `EvidenceAdapter` accepts typed `MarketContext` and retains dict compatibility.
- `IntelligenceService` prefers `runtime_context.market_context` for evidence extraction.
- Existing gamma-flip and IV-skew semantics preserved.
- Local evidence on `c66d971`:
  - focused intelligence: **8 passed in 1.15s**
  - replay/backward: **40 passed, 409 deselected in 7.91s**
  - full regression: **449 passed in 17.40s**

## Latest Live Evidence
2026-09-03 market-hours INDMoney session:
- expected contracts 22
- quotes 22/22
- coverage 100%, COMPLETE
- provider timestamp `2026-09-03 04:11:58.275000+00:00`
- freshness VERIFIED, `0.014676s`
- backend/UI provenance parity PASS
- provider reconciliation PASS
- gaps `[]`
- consecutive OI cycle 1→2: 11 strikes, 22/22 PASS
- integrity SUSPECT due `pe_ltp_below_intrinsic`; do not relabel VALID.

## Canonical Architecture
`INDMoney → market data → AnalyticsPipeline → RuntimeContext.market_context + ctx.analytics compatibility projection → Decision / Intelligence → DashboardData/adapters → Streamlit UI`

Replay:
`recorded snapshot → ReplayLoader → canonical runtime structures → decision/intelligence equivalence`

## Canonical MarketContext Analytics
`dealer`, `dealer_flow`, `liquidity`, `gamma_flip`, `gamma_wall`, `oi_flow`, `iv_skew`, `iv_smile`, `expected_move`, `atr`, `volatility`, `market_structure`, `technical`, `max_pain`, `pcr`, `oi_shift`, `probability`, `signal`, `institutional_score`, `smart_strike`, `trade_plan`, `risk`, `market_map`.

## Next Audit
Do not start a broad feature migration yet. Audit existing downstream consumers field-by-field.

Priority 1: `RuntimeContext.market_context → MarketSnapshot`. `MarketSnapshot` still stores generic `analytics` and DecisionEngine consumes that projection.

Priority 2: `RuntimeContext.market_context → FeatureExtractor → MarketExtractor`. Current `MarketExtractor` still reads `ctx.analytics` for expected move, market structure, technicals, institutional score, probability, PCR, ATR and related values.

Priority 3: `MarketSnapshot → DecisionEngine`. Verify shortcut properties, generic `get()`, and legacy aliases such as `iv` and `oi` do not create wrong mappings.

Priority 4: `DashboardData → adapters → Streamlit`. Dedicated fields are canonical; generic `analytics` remains an established raw analytics display surface. Trace every remaining field before schema changes.

Only derive the next implementation slice from a concrete, reproducible correctness gap. Do not infer end-to-end completion from engine existence or pytest alone.

## Engineering Rules
- Audit first; no invented scope or evidence.
- Canonical backend is authoritative.
- No fabricated/masked data.
- Freshness and integrity remain independent.
- Direction and actionability remain independent.
- Historical recommendations are diagnostic, not live vetoes.
- Gamma flip is regime/level evidence, not directional evidence.
- IV skew mapping is a project heuristic.
- Live-provider failures must not contaminate tests.
- Every behavior change gets regression coverage.
- Never mark green without actual evidence.
- Do not reset/clean unrelated local working-tree changes.
