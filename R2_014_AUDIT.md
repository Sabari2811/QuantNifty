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

## R2-014 Slice 2 — Canonical Context → Snapshot / Replay Boundary Audit

### Audit status

**Baseline:** audit-complete / implementation-ready for a narrow persistence-contract slice.

The Slice 1 implementation establishes a typed canonical analytics surface, but the snapshot boundary does **not** persist `MarketContext` itself. `SnapshotRecorder` persists a separate `analytics` payload plus runtime/decision/explanation/intelligence and the option-chain/greeks frames; `ReplayLoader` restores those same artifacts into `ReplaySnapshot`. This means typed `MarketContext` completeness alone does not prove that every canonical analytics field survives recording/replay. fileciteturn95file0 fileciteturn93file0

### Evidence-led findings

1. **Snapshot model boundary:** `ReplaySnapshot` has an `analytics: dict` payload rather than a `MarketContext` field. fileciteturn93file0
2. **Recorder boundary:** `SnapshotRecorder.save()` writes `ctx.analytics` to `analytics.json`; it does not serialize `ctx` or `ctx.market_context` wholesale. Dataclass values are converted with `asdict()` only when the object passed to `_save_json()` is itself a dataclass. fileciteturn95file0
3. **Replay boundary:** `ReplayLoader.load()` restores `analytics.json` verbatim as a dictionary and separately restores decision, explanation, typed intelligence, option chain, greeks, and provenance. No `MarketContext` reconstruction occurs. fileciteturn94file0
4. **Manifest contract:** `SnapshotManifest` defines `analytics.json` as the canonical analytics artifact and has no separate market-context artifact. fileciteturn96file0
5. **Risk:** the newly typed fields are only replay-safe if the runtime `ctx.analytics` payload contains them. The current recorder/loader contract does not itself assert parity between `MarketContext` analytics fields and the persisted analytics artifact.

### Slice 2 scope decision

**Approved first implementation slice:** add a deterministic contract test at the recorder boundary that proves the canonical analytics surface is persisted from `ctx.analytics` and survives `ReplayLoader` restoration without key loss. The test must use representative values for all fields newly canonicalized in Slice 1 and must not require a live provider session.

This does **not** redesign the snapshot format or add a redundant `MarketContext` file. The existing `analytics.json` artifact remains authoritative unless future evidence demonstrates a need for a separate typed-context artifact.

### Explicit non-goals

- No provider/network changes.
- No analytics calculation changes.
- No changes to decision/intelligence semantics or `authoritative_signal` compatibility.
- No UI changes.
- No migration of existing snapshot manifest version unless the persistence contract itself changes.
- No claim that replay reconstructs a `MarketContext`; the current replay contract restores canonical analytics as a dictionary.

### Slice 2 validation plan

- Targeted regression: recorder → analytics.json → ReplayLoader analytics-key preservation using a deterministic fake runtime context.
- Backward compatibility: existing replay loader behavior for partial/legacy artifacts must remain unchanged.
- Full regression: required after implementation.
- Runtime/live provider: not required for this pure persistence-contract test; existing live evidence remains historical R2-013 evidence.

### Slice 2 exit criteria

- [ ] Contract test committed.
- [ ] Targeted regression passes in the repository runtime.
- [ ] Full regression passes in the repository runtime.
- [ ] No existing replay/provenance/Decision ↔ Intelligence contract regresses.
- [ ] Master checklist updated from actual evidence only.
- [ ] Project state updated from actual implementation/test evidence.

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
