# QuantNifty Project Continuation State

> **Purpose:** Permanent handoff document for continuing QuantNifty in a new ChatGPT conversation without relying on conversation history. Treat this file, Git history, source code, tests, and fresh runtime evidence as the authoritative project record.

## 1. Current State

- Repository: `Sabari2811/QuantNifty`
- Current branch: `r2-011-canonical-snapshot-provenance`
- Project: QuantNifty / NiftySignalEngine
- Local Windows workspace: `D:\Projects\NiftySignalEngine`
- Python environment: project `venv`, PowerShell
- Provider: INDMoney / INDstocks
- Primary objective: production-grade NIFTY options analytics, decision intelligence, live validation, replay, and dashboard with canonical backend data and no silent/wrong UI mappings.
- **Working-tree note:** the user has local uncommitted/untracked files, including generated audit/search artifacts, backups, and a modified `data/instruments/fno.csv`. These are not part of the committed continuation state and must not be assumed to be project source-of-truth without inspection.

## 2. Non-Negotiable Engineering Rules

1. **Audit first.** Do not invent scope, architecture, data, or evidence.
2. **Gap-free workflow.** Every backend capability that matters to the product must have an explicit disposition: implemented/validated, intentionally deferred, or explicitly unsupported.
3. **Canonical backend is authoritative.** UI must consume canonical DashboardData/adapters; never silently recompute displayed values from thresholds or duplicate logic.
4. **No fabricated data.** Missing contracts/values must remain represented as missing/unknown/unavailable according to the established contract.
5. **Provenance is first-class.** Coverage, integrity, freshness, provider source, timestamps, counts, and reasons remain independent dimensions.
6. **Freshness is not integrity.** A fresh quote can still be SUSPECT. Do not convert SUSPECT to VALID merely to make a gate green.
7. **Direction is not actionability.** WAIT can be direction-consistent but non-actionable. Intelligence must not be treated as a veto unless the semantic contract says so.
8. **Historical recommendations are diagnostic context.** They cannot silently veto an otherwise direction-consistent live Decision.
9. **Gamma flip is GEX regime/level evidence, not directional BUY/SELL evidence.**
10. **IV skew directional mapping is a project strategy heuristic**, not a standalone market theorem.
11. **Live-provider failures must not contaminate unit/integration tests.** Live networking must be explicitly enabled/configured.
12. **Every production change gets regression coverage where behavior changes.**
13. **Do not mark a checklist item green without actual evidence.**
14. **Prefer exact runtime evidence over assumptions.**
15. **Do not treat local generated artifacts/backups as authoritative code unless the audit explicitly promotes them.**
16. **Do not clean/revert unrelated user working-tree changes blindly.** First inventory and classify them.

## 3. Completed Major Milestones

### R2-011 — Canonical Snapshot / Replay

Completed and validated:
- Canonical snapshot provenance
- Intelligence artifact persistence
- ReplayLoader intelligence restoration
- Typed replay intelligence contract
- Replay decision equivalence
- Replay intelligence equivalence
- Real recorded snapshot replay equivalence
- Zero-drift real replay gate
- Replay backward compatibility for legacy snapshots and authoritative decision signal handling

### R2-013 — Live Backend Validation / Backend → UI Reconciliation

Closed and fully green in `R2_MASTER_CHECKLIST.md` with the explicit integrity caveat described below.

### R2-014 — Audit Baseline / Canonical Analytics Context

**Slices 1–5 implemented. Slice 5 is fully regression-green locally. The overall R2-014 release gate remains open until the next canonical downstream consumer audit is completed.**

Slice 1:
- Typed `MarketContext` declares the complete 22-field analytics result surface populated by `AnalyticsPipeline.run()`.

Slice 2:
- Existing `ctx.analytics` → snapshot/replay JSON boundary retained for backward compatibility.
- Deterministic recorder → replay regression covers all 22 canonical analytics fields.

Slice 3:
- Audited and regression-proved `AnalyticsPipeline.run()` → `LiveEngine.ctx.analytics` → `MarketSnapshot.analytics` → `SnapshotRecorder.analytics.json` → `ReplayLoader.analytics`.

Slice 4:
- `RuntimeContext.market_context` is now a typed `MarketContext` canonical runtime field.
- `LiveEngine` promotes the pipeline-returned `MarketContext` into `RuntimeContext.market_context` and retains `ctx.analytics` as the compatibility/serialization projection.
- Dedicated `DashboardData` analytics fields now read from the typed canonical runtime context rather than directly from the generic analytics dictionary.
- Regression coverage validates typed runtime creation, promotion contract, and the updated intelligence-test fakes.

Slice 5:
- Normal replay now reconstructs typed `MarketContext` from recorded analytics.
- Snapshot `spot` and `greeks` remain authoritative replay identity fields.
- Typed reconstruction is centralized in `MarketContext.from_analytics()`.
- `REPLAY_RECOMPUTE` retains recomputed analytics/context for audit diagnostics.
- Recorded analytics remain the canonical replay/UI typed context when the recorded projection exists, preventing recomputation drift from becoming a second canonical surface.
- Recorded ↔ recomputed typed-context parity is explicit as `replay_analytics_equivalence` and is intentionally separate from decision/intelligence equivalence.

**Authoritative post-Slice-5 local evidence (2026-09-03):**
- Targeted replay/runtime promotion suite: **3 passed in 1.11s** on `e69a5e5`
- Replay/backward-compatibility suite: **40 passed, 408 deselected in 7.14s** on `e69a5e5`
- Full regression: **448 passed in 15.90s** on `e69a5e5`

These are the current authoritative local validation results for R2-014 Slice 5.

## 4. Latest Verified Live Evidence

Fresh market-hours INDMoney validation on **2026-09-03**:

- Option contracts expected: **22**
- Quotes received: **22/22**
- Coverage: **100%**
- Coverage status: **COMPLETE**
- Provider timestamp: `2026-09-03 04:11:58.275000+00:00`
- Freshness: **VERIFIED**
- Measured freshness: **0.014676s**
- Backend/UI provenance parity: **PASS**
- Provider reconciliation: **PASS**
- Gaps: `[]`
- Consecutive OI: cycle 1 → cycle 2, 11 strikes, **22/22 PASS**, `LIVE_OI_CONSECUTIVE=PASS`

Important integrity caveat:
- Integrity status was **SUSPECT**, reason: `pe_ltp_below_intrinsic`.
- This is intentionally retained as a real data-quality finding.
- It does **not** invalidate freshness or coverage evidence and must not be silently changed to VALID.

Historical candle evidence from the earlier post-market UI session was STALE and is not to be reused as current freshness evidence. The timestamp-bearing market-hours session above is the authoritative freshness evidence.

## 5. Regression Baseline

Current post-Slice-5 full regression:
- **448 passed in 15.90s** on `e69a5e5`

Current Slice-5 targeted replay/runtime promotion regression:
- **3 passed in 1.11s** on `e69a5e5`

Current replay/backward-compatibility regression:
- **40 passed, 408 deselected in 7.14s** on `e69a5e5`

Previous Slice-4 baseline:
- **444 passed in 19.73s**

Previous historical R2-013 final baseline:
- **435 passed in 19.47s**

Do not use older baselines as validation of current R2-014 changes.

## 6. Canonical Architecture / Data Flow

The intended flow is:

`INDMoney REST/WebSocket`
→ `market data pipeline / provider normalization`
→ `canonical MarketContext / DashboardData`
→ `analytics pipeline`
→ `decision + intelligence`
→ `dashboard adapters`
→ `Streamlit UI`

Replay path:

`recorded canonical snapshot`
→ `ReplayLoader`
→ `canonical runtime structures`
→ `decision/intelligence equivalence`
→ validation gate

UI rule:

`canonical backend value`
→ `adapter`
→ `UI`

Never:

`raw UI widget logic`
→ independent recomputation

## 7. Current Analytics Surface

The analytics pipeline currently instantiates/uses major engines including:

- Gamma exposure
- Gamma flip
- Gamma wall
- Dealer position
- Dealer flow
- Delta exposure
- Vanna
- Charm
- Liquidity
- OI flow
- IV skew
- IV smile
- Expected move
- Max pain
- PCR
- Market structure
- ATR / volatility
- Technical analysis
- Probability
- Signal
- Institutional score
- Smart strike
- Trade plan
- Risk
- Market map

Presence of an engine does not prove end-to-end completion. Each capability must be audited through canonical context, persistence/replay, decision/intelligence use, DashboardData, UI mapping, tests, and live evidence where applicable.

## 8. Current Analytics Pipeline Ordering

The current pipeline broadly performs:

1. Gamma exposure
2. Gamma flip / wall
3. Dealer analysis
4. Delta/Vanna/Charm exposure
5. Dealer flow
6. Liquidity
7. OI flow
8. IV skew/smile
9. Expected move / Max pain / PCR
10. ATR / volatility
11. Market structure
12. Technical analysis from candles when available
13. Probability
14. Signal
15. Institutional score
16. Smart strike
17. Trade plan
18. Risk
19. MarketContext construction
20. Market map construction

When changing this order, explicitly audit downstream dependencies and snapshot/replay/UI consequences.

## 9. Important Semantic Contracts

### Decision ↔ Intelligence
- `consistent`
- `actionable`
- `vetoed`
- `semantic_status`
- `decision_signal`
- `intelligence_recommendation`
- `intelligence_direction`
- `reason`

WAIT is allowed to be:
- consistent = true
- actionable = false
- vetoed = false

### Decision signal provenance
`Decision.authoritative_signal` captures the canonical decision signal before execution mutation. Runtime reconciliation prefers this authoritative value.

### Gamma flip
Gamma flip remains GEX regime/level evidence. It must not be converted into directional evidence.

### Historical recommendation
HistoricalEvidence is diagnostic context, not a live veto.

## 10. Provenance Contract

Canonical provenance independently represents source, acquired_at, provider_timestamp, expected/received/missing counts, coverage, freshness, integrity, reasons, and related data-quality dimensions. UI must preserve these independently.

Correct live evidence can simultaneously be:

`freshness=VERIFIED`
`coverage=COMPLETE`
`integrity=SUSPECT`
`reconciliation=PASS`

## 11. Important Files / Areas

- `R2_MASTER_CHECKLIST.md`
- `QUANTNIFTY_PROJECT_STATE.md`
- `core/runtime_context.py`
- `models/market_context.py`
- `analytics/analytics_pipeline.py`
- `engine/live_engine.py`
- `analytics/market_snapshot/market_snapshot.py`
- `dashboard/dashboard_controller.py`
- `models/dashboard_data.py`
- `dashboard/decision_adapter.py`
- `dashboard/intelligence_adapter.py`
- `decision/decision_engine.py`
- `simulation/replay_equivalence.py`
- `simulation/replay_loader.py`
- `recording/snapshot_recorder.py`
- `tests/`

## 12. R2-014 Current Audit Disposition / Next Work

### Slice 5 disposition
Slice 5 is **green**. The previous replay parity failure was treated as a contract discovery, not suppressed as a test nuisance. Real snapshot recomputation showed that recompute can lack historical dependencies needed to exactly reproduce every recorded analytics field. Therefore:

- recorded analytics remain the canonical replay/UI surface;
- recomputed typed analytics/context remain available for diagnostics;
- `replay_analytics_equivalence` exposes recorded ↔ recomputed drift explicitly;
- decision/intelligence replay equivalence remains a separate gate.

### Next audit — downstream canonical consumer boundary

Do not implement a new feature yet. The next audit must trace the already-existing canonical context through all downstream consumers and identify concrete source-of-truth gaps before a new slice is defined.

Highest-priority path:

`RuntimeContext.market_context`
→ `MarketSnapshot / replay`
→ `DecisionEngine / Intelligence`
→ `DashboardData / adapters`
→ `Streamlit UI`

Audit questions:
1. **Live semantic identity:** for every canonical `MarketContext` field, verify whether `ctx.analytics[field]` and `ctx.market_context.<field>` are semantically identical at the live handoff boundary, including nested structures and special values.
2. **Replay identity:** verify all replay modes and degraded paths, including `REPLAY_FAST`, normal replay, `REPLAY_RECOMPUTE`, missing analytics, and legacy snapshots.
3. **MarketSnapshot boundary:** determine whether its generic `analytics` dictionary is intentionally a compatibility projection or an untracked second canonical source, and inventory every downstream consumer that reads it.
4. **Decision source-of-truth:** verify which snapshot fields feed `DecisionEngine` and whether any decision logic bypasses `MarketContext` semantics or depends on legacy aliases.
5. **Intelligence source-of-truth:** verify intelligence consumers receive the canonical runtime artifact and do not silently reconstruct analytics from alternate surfaces.
6. **DashboardData coverage:** inventory every canonical analytics field and record one disposition: dedicated DashboardData field, intentionally generic `analytics`, intentionally not UI-facing, or missing mapping.
7. **Adapter/UI mapping:** trace dedicated and generic fields into `dashboard/*` adapters and Streamlit components; identify duplicate computations, hardcoded defaults, stale field names, or unsupported assumptions.
8. **Remaining analytics:** explicitly disposition `gamma_flip`, `gamma_wall`, `oi_flow`, `iv_skew`, `iv_smile`, `atr`, `volatility`, `technical`, `oi_shift`, `market_map`, `smart_strike`, and any other declared canonical field.
9. **Tests:** for every concrete correctness gap found, add or strengthen a focused regression before implementation is considered complete.

### Audit deliverable

The next implementation slice should be derived only from findings that are concrete, reproducible, and attributable to a specific canonical boundary. Do not promote an engine into scope merely because it exists in `analytics/`.

## 13. Known Intentional Caveats / Do Not Misread

- `SUSPECT` integrity is not the same as stale or incomplete data.
- REST quotes without provider timestamps must remain `FRESHNESS_UNVERIFIED`.
- Historical candle age must be evaluated from its provider timestamp.
- WebSocket timeout must not fabricate a fresh provider timestamp.
- Gamma flip is not directional evidence.
- Historical recommendation is not a live veto.
- WAIT can be consistent and non-actionable.
- Passing pytest does not prove a fresh live provider session.
- Live provider pass does not prove replay equivalence.
- An engine existing in `analytics/` does not prove end-to-end completion.

## 14. Git / Continuation Procedure

At the start of a new chat:

```powershell
git checkout r2-011-canonical-snapshot-provenance
git pull origin r2-011-canonical-snapshot-provenance
git status
git log -1 --oneline
```

Then read:

```text
QUANTNIFTY_PROJECT_STATE.md
R2_MASTER_CHECKLIST.md
```

Classify the working tree before touching unrelated changes. Do not reset/clean the tree just to create a convenient baseline.

## 15. New-Chat Bootstrap Prompt

> Continue the QuantNifty / NiftySignalEngine project from GitHub repository `Sabari2811/QuantNifty`.
>
> First read `QUANTNIFTY_PROJECT_STATE.md` and `R2_MASTER_CHECKLIST.md` from the current branch. Treat repository, Git history, tests, and fresh runtime evidence as authoritative. Do not ask me to repeat project context.
>
> R2-013 is closed/green with its explicit integrity SUSPECT caveat. R2-014 Slice 1–5 are implemented, with Slice 5 green at targeted **3 passed**, replay/backward **40 passed / 408 deselected**, and full **448 passed** on `e69a5e5`. Do not claim the overall R2-014 release gate is complete yet.
>
> Continue audit-first and gap-free. The next task is to trace the canonical typed `RuntimeContext.market_context` through `MarketSnapshot / replay → DecisionEngine / Intelligence → DashboardData / adapters → Streamlit UI`, including a field-by-field inventory of remaining analytics mappings and legacy generic-analytics consumers. Only implement a new slice after the audit identifies a concrete correctness gap. Preserve all provenance, freshness, integrity, replay, decision/intelligence, and UI canonicality contracts.
