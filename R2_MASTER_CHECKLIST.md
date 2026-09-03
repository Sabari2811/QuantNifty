# QuantNifty Master Validation Checklist

## R2-014 — Audit Baseline / Canonical Analytics Context

### Slice 1 — Typed canonical `MarketContext`
- [x] Declare every analytics result currently attached by `AnalyticsPipeline.run()` in `MarketContext`
- [x] Preserve existing pipeline computations and populate the declared fields without changing analytics semantics
- [x] Add regression coverage for canonical context surface and pipeline population
- [x] Targeted regression pass — 4 passed in 2.81s
- [x] Full regression pass — **441 passed in 21.31s** after fast-forward to `150225c`
- [x] Implementation evidence recorded in repository

### Slice 2 — Canonical Context → Snapshot / Replay
- [x] Snapshot/replay boundary audited
- [x] Existing `ctx.analytics` → `analytics.json` architecture retained; no redundant `MarketContext` artifact
- [x] Deterministic recorder → replay regression covers all 22 canonical analytics fields
- [x] Targeted regression pass — 4 passed in 2.81s
- [x] Replay/backward-compatibility regression pass — 36 passed, 405 deselected in 11.34s
- [x] Full regression pass — **441 passed in 21.31s** after fast-forward to `150225c`
- [x] Implementation evidence recorded in repository
- [ ] Slice 2 release/green gate

### Slice 3 — Runtime Analytics Handoff Audit
- [x] Audited `AnalyticsPipeline.run()` → `LiveEngine.ctx.analytics` → `MarketSnapshot.analytics` → `SnapshotRecorder.analytics.json` → `ReplayLoader.analytics`
- [x] Confirmed production runtime preserves the complete pipeline result in `ctx.analytics`
- [x] Structural regression proves canonical fields are declared, assigned, returned, and preserved by normal runtime handoff
- [x] Targeted Slice 3 regression pass — 6 passed in 2.39s
- [x] Replay/backward-compatibility regression pass — 36 passed, 405 deselected in 11.34s
- [x] Full regression pass — **441 passed in 21.31s** after fast-forward to `150225c`
- [x] Implementation evidence recorded in repository
- [ ] Slice 3 release/green gate

### Slice 4 — Typed MarketContext Runtime Promotion
- [x] Audit confirmed `AnalyticsPipeline.run()` creates a typed `MarketContext` that was previously discarded after the pipeline return
- [x] Add typed `market_context: MarketContext` to `RuntimeContext`
- [x] Promote the pipeline-returned `MarketContext` into `RuntimeContext.market_context`
- [x] Preserve `RuntimeContext.analytics` as the established serialized/backward-compatible projection
- [x] Route dedicated `DashboardData` analytics fields from typed `RuntimeContext.market_context`
- [x] Add regression coverage for typed runtime field and LiveEngine promotion
- [x] Targeted Slice 4 regression — **7 passed in 6.43s**
- [x] Full regression — **444 passed in 19.73s**
- [x] Replay/backward-compatibility regression — **36 passed, 408 deselected in 21.23s**
- [x] Slice 4 release/green gate

### Slice 5 — Replay → Typed MarketContext Canonical Boundary
- [x] Audit identified normal replay restoring `ctx.analytics` while leaving `ctx.market_context` at its default empty typed value
- [x] Normal replay reconstructs typed `MarketContext` from recorded analytics
- [x] Snapshot `spot` and `greeks` remain authoritative replay identity fields
- [x] Centralize typed context reconstruction in `MarketContext.from_analytics()`
- [x] REPLAY_RECOMPUTE retains recomputed analytics/context for audit diagnostics
- [x] Add explicit recorded-analytics ↔ recomputed-typed-context parity diagnostic
- [x] Make recorded analytics the canonical replay/UI context when a recorded projection exists, preventing a recomputation drift from becoming a second source of truth
- [x] Add regression coverage for reconstruction and parity detection
- [ ] Targeted Slice 5 post-fix regression
- [ ] Replay/backward-compatibility regression
- [ ] Full regression
- [ ] Slice 5 release/green gate

### R2-014 Release Gate Status
- [x] Slice 4 release gate previously green — targeted **7 passed**, replay/backward **36 passed / 408 deselected**, full **444 passed**
- [x] Slice 5 targeted reconstruction/parity suite — **4 passed in 1.27s** on commit `e2400e1` before the post-failure parity contract correction
- [ ] Slice 5 replay/backward-compatibility suite green after parity correction
- [ ] Slice 5 full regression green after parity correction
- [ ] Current R2-014 release gate complete

### Slice 5 Failure Evidence / Audit Disposition
The first implementation folded analytics/context parity mismatches into `replay_equivalence`. The user's authoritative local run exposed **1 failure / 39 passed / 408 deselected** in the replay/backward suite and **1 failure / 447 passed** in the full suite. The failing real-snapshot gate reported drift across derived analytics including OI-flow, technical, probability, market-map, wall/void, and other values. The captured OI log also showed recomputation entering `AWAITING_PREVIOUS_SNAPSHOT`, demonstrating that replay recomputation does not necessarily possess every historical dependency required to reproduce the recorded analytics artifact exactly.

Disposition: analytics/context parity is now an explicit **diagnostic parity result** (`replay_analytics_equivalence`) rather than a decision/intelligence veto. During `REPLAY_RECOMPUTE`, the recomputed context remains available for audit, while the recorded analytics projection is restored into the canonical typed `market_context` so replay does not silently create two competing canonical surfaces. The existing decision/intelligence equivalence contract remains independent and continues to be the replay output gate. This correction must be validated by the next local targeted → replay/backward → full sequence before Slice 5 can be marked green.

### Evidence note
Pre-Slice-4 full local validation was run from `D:\Projects\NiftySignalEngine` after fast-forwarding the local branch from `138c5bc` to `150225c`: `pytest -q` → **441 passed in 21.31s**. After Slice 4 and its regression fixes, the user pulled branch tip `243cf1c` and reran all required suites locally: targeted canonical-context suite → **7 passed in 6.43s**; replay/backward-compatibility suite → **36 passed, 408 deselected in 21.23s**; full regression → **444 passed in 19.73s**. Slice 5 initial targeted suite then passed **4 in 1.27s**, but the first parity implementation caused the real recorded-snapshot replay gate to fail as documented above. These failure results are authoritative and are intentionally not treated as green validation for the corrected Slice 5 implementation.

### Integrity / scope reminder
R2-013 remains historically green with fresh 2026-09-03 live evidence and explicit `integrity_status=SUSPECT` / `pe_ltp_below_intrinsic`. That data-quality caveat is unchanged and must not be relabeled as VALID. R2-014 remains audit-first; no live-provider or Streamlit runtime gate is inferred from pytest evidence alone.
