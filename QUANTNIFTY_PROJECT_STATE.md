# QuantNifty Project Continuation State

> **Purpose:** Permanent handoff document for continuing QuantNifty in a new ChatGPT conversation without relying on conversation history. Treat this file, Git history, source code, tests, and fresh runtime evidence as the authoritative project record.

## 1. Current State

- Repository: `Sabari2811/QuantNifty`
- Current branch: `r2-011-canonical-snapshot-provenance`
- Current HEAD at handoff baseline: `bf9ab36103f3379d4d3f6b2403a34569c18e43fc`
- Latest continuation-state commit after adding this document: `ccffb8b` (`docs: add QuantNifty project continuation state`)
- Project: QuantNifty / NiftySignalEngine
- Local Windows workspace: `D:\Projects\NiftySignalEngine`
- Python environment: project `venv`, PowerShell
- Provider: INDMoney / INDstocks
- Primary objective: production-grade NIFTY options analytics, decision intelligence, live validation, replay, and dashboard with canonical backend data and no silent/wrong UI mappings.
- **Working-tree note at handoff:** the user has local uncommitted/untracked files, including generated audit/search artifacts, backups, and a modified `data/instruments/fno.csv`. These are not part of the committed continuation state and must not be assumed to be project source-of-truth without inspection.

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

**Closed and fully green in `R2_MASTER_CHECKLIST.md`.**

Completed:
- Live spot and option-chain acquisition validation
- Coverage and consecutive-cycle validation
- Missing-contract denominator preservation
- NIFTY expiry validation against refreshed F&O master
- Provider timestamp propagation
- Quote freshness semantics including UNVERIFIED/future timestamp handling
- Timestamp-bearing INDstocks WebSocket feed
- Live quote freshness validation
- Consecutive OI validation
- Option-chain integrity validator with INVALID vs SUSPECT separation
- Live Greeks for selected expiry
- Raw-provider analytics reconciliation
- Decision/Intelligence reconciliation
- Decision ↔ Intelligence semantic model
- Canonical backend → DashboardData/UI reconciliation
- Authoritative Greek projection into option-chain UI by contract identity
- Provenance/integrity/freshness UI mapping
- Canonical decision/intelligence adapters
- Streamlit runtime reconciliation
- Full regression baseline after final R2-013 code changes

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

Historical candle evidence from the earlier post-market UI session was STALE and is not to be reused as current freshness evidence. The timestamp-bearing market-hours session is the authoritative freshness evidence above.

## 5. Regression Baseline

Latest recorded full regression:

- **435 passed in 19.47s**
- Recorded after final R2-013 degraded-market test contract fixes.

Targeted regression coverage exists for:
- WebSocket parsing/freshness
- Future provider timestamps
- Option-chain integrity/degraded data
- Live provider reconciliation
- Live OI consecutive cycles
- Decision/Intelligence semantics
- Gamma-flip evidence semantics
- Historical recommendation semantics
- Authoritative decision signal preservation
- Replay authoritative-signal compatibility
- Canonical live Greeks projection
- Option-chain enriched analytics projection
- UI reconciliation
- Market banner/regime degraded contracts

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

The repository contains a broad analytics surface, but **presence of an engine does not mean it is fully canonical, validated, replayable, or UI-reconciled**. Audit each capability before declaring it complete.

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

The established semantic model includes:

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

This is intentional.

### Decision signal provenance

`Decision.authoritative_signal` was added so the canonical decision signal is captured before execution mutation. Runtime reconciliation prefers this authoritative value. Do not regress to inferring the displayed decision signal from post-execution state.

### Gamma flip

Gamma flip remains GEX regime/level evidence. It must not be converted into BULLISH/BEARISH directional evidence merely because a consumer expects a direction.

### Historical recommendation

HistoricalEvidence recommendation is diagnostic context. A historical WAIT must not override a direction-consistent live decision.

## 10. Live Provider Details

INDMoney/INDstocks WebSocket implementation:

- Price endpoint: `wss://ws-prices.indstocks.com/api/v1/ws/prices`
- Authentication uses the provider access token through the documented Authorization header.
- Provider WebSocket timestamps are epoch milliseconds and are normalized to UTC.
- `LiveQuoteTick` retains provider timestamp information.
- Freshness assessment explicitly handles clock skew, fresh, stale, and future timestamps.
- Coordinator matches requested instruments and records receive/acquisition times.

Instrument convention already established:
- REST option instruments use the provider's REST format.
- WebSocket instruments use the WebSocket segment/token format.
- NIFTY index WebSocket token must be configured/looked up explicitly; do not invent it.

Known robustness consideration:
- The live pipeline has a controlled WebSocket timeout fallback. If further hardening connection/authentication failure behavior, preserve the rule that optional live feed failure must not silently become fake freshness.

## 11. Provenance Contract

Canonical provenance independently represents:

- source
- acquired_at
- provider_timestamp
- expected count
- received count
- missing count
- coverage ratio/status
- freshness status
- freshness_verified
- freshness seconds/age
- integrity status
- integrity reasons
- other explicit data-quality reasons

The UI must preserve these dimensions independently.

Current live evidence is an example of the correct distinction:

`freshness=VERIFIED`
`coverage=COMPLETE`
`integrity=SUSPECT`
`reconciliation=PASS`

Do not collapse this into one generic health flag.

## 12. Important Files / Areas

Key areas include:

- `R2_MASTER_CHECKLIST.md` — master validation checklist
- `QUANTNIFTY_PROJECT_STATE.md` — permanent continuation/handoff state
- `providers/indmoney_websocket.py` — timestamp-bearing WebSocket feed
- `providers/live_quote_coordinator.py` — bounded live quote collection
- `engine/market_data_pipeline.py` — canonical market-data acquisition/provenance
- `dashboard/live_provider_reconciliation.py` — backend/UI/provider reconciliation
- `dashboard/live_reconciliation.py` — live dashboard reconciliation
- `dashboard/provenance_adapter.py` — provenance mapping
- `dashboard/components/option_chain.py` — authoritative option-chain/Greek projection
- `analytics/analytics_pipeline.py` — broad analytics orchestration
- `analytics/intelligence/decision_consistency.py` — Decision ↔ Intelligence semantics
- `analytics/intelligence/synthesis/family_aggregator.py` — evidence family aggregation
- `simulation/replay_equivalence.py` — replay equivalence
- `tests/` — regression and runtime contract tests
- `tools/validate_live_provider_reconciliation.py` — fresh live provider reconciliation runner
- `tools/validate_live_oi_consecutive.py` — consecutive OI validation
- `tools/inspect_live_decision_intelligence.py` — live decision/intelligence inspection
- `dashboard/decision_intelligence_status.py` — decision/intelligence status presentation

## 13. R2-013 Final Checklist Status

`R2_MASTER_CHECKLIST.md` records R2-013 as fully green.

Release-gate items are all checked, including:
- fresh live-session backend validation
- backend → UI reconciliation
- Decision ↔ Intelligence semantic reconciliation
- targeted tests
- real snapshot replay
- full regression
- master checklist fully green

The integrity SUSPECT condition remains explicitly documented rather than hidden.

## 14. R2-014 Status

There is **no explicit R2-014 specification in the repository at this handoff**.

Therefore the next chat must **not invent an R2-014 feature list**.

Required next action:

1. Audit the repository at the current commit.
2. Inventory analytics engines and their consumers.
3. Map each important analytics capability through:
   - provider input
   - canonical context
   - snapshot persistence
   - replay restoration
   - decision/intelligence consumption
   - DashboardData
   - UI adapter/display
   - tests
   - live evidence where applicable
4. Inventory and classify uncommitted/untracked local artifacts before modifying or deleting any of them.
5. Identify the highest-value incomplete canonical path.
6. Define R2-014 scope and checklist from that audit.
7. Implement the first justified slice.
8. Add regression tests.
9. Run targeted tests and full regression.
10. Perform live validation when the capability depends on live data.
11. Update `R2_MASTER_CHECKLIST.md` only from actual evidence.
12. Update this state file whenever a major milestone, architecture decision, semantic contract, release gate, or known caveat changes materially.

Do not skip the audit merely because an engine already exists in the codebase.

## 15. Suggested First R2-014 Audit Candidates

These are **audit candidates, not approved scope**:

- analytics currently present but not clearly represented in canonical snapshot/replay
- analytics present in backend but not fully mapped to DashboardData/UI
- institutional score / signal / smart-strike / trade-plan provenance and replay equivalence
- volatility/technical analytics canonicalization
- deeper raw-provider analytics reconciliation beyond the already validated 15 fields
- option-chain integrity SUSPECT investigation for `pe_ltp_below_intrinsic`
- live WebSocket failure/authentication fallback hardening

Rank candidates by architectural risk and user-visible correctness, not by feature novelty.

## 16. Known Intentional Caveats / Do Not Misread

- `SUSPECT` integrity is not the same as stale or incomplete data.
- REST quotes without provider timestamps must remain `FRESHNESS_UNVERIFIED`.
- Historical candle age must be evaluated from its provider timestamp; an old candle cannot be called fresh merely because it was recently acquired.
- WebSocket timeout must not fabricate a fresh provider timestamp.
- Gamma flip is not directional evidence.
- Historical recommendation is not a live veto.
- WAIT can be consistent and non-actionable.
- A passing UI test does not automatically prove a fresh live provider session.
- A live provider pass does not automatically prove replay equivalence.
- An engine existing in `analytics/` does not prove end-to-end completion.

## 17. Git / Continuation Procedure

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

The branch may advance after this document was written. Prefer the latest branch HEAD and re-read this file before proceeding. At the moment of the continuation-state pull observed by the user, the local branch was synchronized at:

```text
ccffb8b docs: add QuantNifty project continuation state
```

The previous R2-013 closure evidence was based on `bf9ab36` and should remain interpreted as historical evidence unless newer runtime evidence supersedes it.

## 18. New-Chat Bootstrap Prompt

Copy this into the first message of the new chat:

> Continue the QuantNifty / NiftySignalEngine project from the GitHub repository `Sabari2811/QuantNifty`.
>
> First read `QUANTNIFTY_PROJECT_STATE.md` and `R2_MASTER_CHECKLIST.md` from the current branch. Treat the repository, Git history, tests, and fresh runtime evidence as authoritative. Do not ask me to repeat project context.
>
> Current handoff branch is `r2-011-canonical-snapshot-provenance`; the branch may have advanced beyond the historical handoff commit, so use the latest commit and re-read the state file.
>
> R2-013 is closed and fully green based on the recorded evidence. Preserve all established provenance, freshness, integrity, Decision ↔ Intelligence, replay, and backend → UI contracts. Do not invent R2-014 scope. First audit the current repository, including the local working tree classification where applicable, identify the highest-value incomplete canonical path, create the R2-014 audit/checklist baseline, and then implement the first justified slice with regression and runtime validation. Maintain the gap-free, audit-first workflow and do not mark anything green without evidence.

## 19. Handoff Integrity

This file is itself a continuity aid. It must be updated whenever a major milestone, architecture decision, semantic contract, release gate, or known caveat changes materially.

**Current handoff conclusion:** R2-013 is closed based on recorded evidence. The next chat should begin with a repository audit for R2-014 rather than feature invention, while preserving and classifying any user-local uncommitted/untracked work before making destructive changes.
