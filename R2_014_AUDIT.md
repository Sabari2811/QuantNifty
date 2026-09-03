# R2-014 Audit Baseline

## Audit status

**Baseline:** audit-complete / implementation-ready
**Branch:** `r2-011-canonical-snapshot-provenance`
**Audited commit:** `1fd69d3c2d2c3f4aba2ded67364efd3efbcec744`
**Previous milestone:** R2-013 closed and fully green per `R2_MASTER_CHECKLIST.md`

R2-014 scope is derived from the current repository audit. No feature scope is imported from the historical handoff candidates without evidence.

## Working-tree classification

The repository continuation state records that the user's local Windows workspace contains uncommitted/untracked generated audit/search artifacts, backups, and a modified `data/instruments/fno.csv`. The GitHub repository view cannot inspect that separate local working tree, so **local working-tree state is NOT VERIFIED in this session**. No local artifact is deleted, reverted, promoted, or treated as source-of-truth by this work.

Committed repository state remains the only implementation source used for this baseline.

## Repository / architecture audit

The current analytics pipeline instantiates and executes a broad surface: gamma exposure/flip/wall, dealer/dealer-flow, delta/vanna/charm, liquidity, OI flow, IV skew/smile, expected move, max pain, PCR, ATR/volatility, market structure, technical analysis, probability, signal, institutional score, smart strike, trade plan, risk, and market map.

The pipeline then constructs `MarketContext` and also returns a dictionary containing the completed analytics. The audit found a canonicalization gap at this boundary:

- `models/market_context.py` declares only a subset of the analytics surface.
- `analytics/analytics_pipeline.py` assigns several additional attributes dynamically after constructing `MarketContext`.
- The same pipeline returns those values as explicit dictionary keys, demonstrating that they are real pipeline outputs rather than speculative future fields.
- Missing declared fields include at least `dealer_flow`, `liquidity`, `expected_move`, `volatility`, `technical`, `institutional_score`, and `market_map`.
- This creates a typed-contract gap: the internal canonical context can silently drift from the actual pipeline output surface even while existing downstream tests remain green.

This is the highest-value first slice because it sits directly on the canonical analytics boundary and reduces structural drift before extending snapshot/replay/UI coverage further.

## Candidate disposition

| Candidate | Disposition | Reason |
|---|---|---|
| Typed canonical `MarketContext` completeness | **R2-014 Slice 1 — APPROVED** | Directly evidenced mismatch between pipeline outputs and typed context; low semantic risk; foundational to later snapshot/replay work |
| Institutional score / smart-strike / trade-plan provenance + replay | Deferred to follow-on slice | Important, but first remove the typed canonical boundary gap |
| Volatility/technical snapshot/replay/UI canonicalization | Deferred to follow-on slice | Depends on stable canonical context surface |
| Deeper raw-provider analytics reconciliation | Deferred | R2-013 already covers 15 raw-provider-derived fields; expand only after boundary audit |
| `pe_ltp_below_intrinsic` SUSPECT investigation | Deferred | Real data-quality finding, but unrelated to the canonical context type gap and must remain explicitly SUSPECT |
| WebSocket failure/authentication hardening | Deferred | Existing fallback semantics are covered; no new failure evidence in this audit |

## R2-014 Slice 1 contract

1. `MarketContext` declares every analytics result currently attached by `AnalyticsPipeline.run()`.
2. The pipeline continues to populate those fields from the exact result objects it already computes; no new analytics logic is introduced.
3. Existing provenance, freshness, integrity, Decision ↔ Intelligence, replay, and UI contracts are unchanged.
4. Regression coverage proves the newly canonicalized fields are declared and populated at the pipeline context boundary.
5. No checklist item is marked green until the implementation is validated by tests/runtime evidence.

## Validation plan

### Targeted
- MarketContext schema/canonical-surface regression.
- Analytics pipeline context population regression.
- Existing replay/provenance tests touching canonical context, if affected.

### Full regression
- Run the complete pytest suite after the slice.

### Runtime
- Because Slice 1 is a typed/internal canonicalization change with no provider or UI behavior change, a new live provider session is **not required to prove the slice itself**. Existing fresh R2-013 live evidence remains historical release evidence and must not be relabeled as new R2-014 runtime evidence.
- If implementation changes any serialization, replay, DashboardData, or UI path unexpectedly, the scope must be re-audited before proceeding.

## Exit criteria for Slice 1

- [ ] Implementation committed.
- [ ] Targeted regression passes.
- [ ] Full regression passes.
- [ ] No established semantic/provenance contracts regress.
- [ ] R2-014 master checklist updated only with actual evidence.
- [ ] Project state updated with the resulting commit and evidence.
