# QuantNifty — Master Progress & Continuation Tracker

**Last updated:** 2026-09-08
**Repository:** `Sabari2811/QuantNifty`
**Authoritative branch:** `main`
**Current verified HEAD:** `1c3bbeceffcf883e9afe21a56f33da192f346f27`
**Current state:** Backend implementation complete / regression green / production live certification pending

> This file is the primary continuation tracker for future ChatGPT sessions. Read it before starting new work. Do not restart completed architecture work unless new evidence requires it.

---

## 1. Project Summary

QuantNifty is a modular NIFTY options market-intelligence platform covering:

- market-data providers and instrument management
- live option-chain analytics
- Greeks, GEX, DEX, Gamma Walls and Gamma Flip
- OI flow, IV/skew and market-structure analytics
- expected move, Max Pain and PCR
- dealer/institutional intelligence
- direction-aware scoring and decision intelligence
- risk and trade validation
- execution planning and safe execution lifecycle handling
- paper trading
- replay / historical simulation / backtesting foundations
- canonical DashboardData-driven dashboard architecture
- provenance, freshness and quote-integrity controls
- monitoring and health infrastructure
- Adaptive Brain / learning infrastructure
- live-session evidence and validation
- production hardening and durable audit/idempotency foundations

The project is being developed as a production-grade institutional market-intelligence system, with strict separation between **direction**, **actionability**, **risk permission**, **execution**, **historical replay**, and **learning/intelligence**.

---

## 2. Authoritative Source / Repository Rules

### QuantNifty

- Repository: `Sabari2811/QuantNifty`
- Branch: **`main`**
- `main` is the authoritative code branch for continuation.
- Current HEAD: **`1c3bbeceffcf883e9afe21a56f33da192f346f27`**
- Latest commit: `fix: use available rfc3987 syntax release`

### Separate project — DO NOT TOUCH

`Sabari2811/QuantNifty-Next` is a separate project.

- Do not modify its code.
- Do not modify its environment variables.
- Do not use its Render/Postgres resources for QuantNifty.
- Do not merge or copy QuantNifty-Next changes into QuantNifty unless explicitly requested.

---

## 3. Engineering Operating Rules

Every change follows:

1. Inspect current repository state.
2. Identify the exact gap.
3. Make **one focused change**.
4. Add/update targeted regression tests.
5. Run targeted tests.
6. Run full regression before release.
7. Review the diff for unintended changes.
8. Commit to `main`.
9. Deploy only when the change is ready.
10. Validate deployment/runtime evidence.

### Architecture guardrails

- One canonical owner per domain concept.
- `DashboardData` is authoritative for dashboard rendering.
- UI adapters/presenters are read-only mappings; they must not silently recompute canonical analytics.
- Direction is not actionability.
- Intelligence may inform but must not silently veto an authoritative live direction/decision.
- Gamma Flip is regime/level evidence, not a standalone trading signal.
- Historical/replay logic must not silently veto live direction.
- Freshness and integrity are separate dimensions.
- Missing/invalid/suspect values fail closed and are explicitly represented.
- Execution outcomes of `UNKNOWN` require reconciliation; they must not be treated as success or ordinary failure.
- Audit history is append-only.
- Idempotency must survive process restart when durable audit storage is configured.
- No real-money order placement from tests.
- Deployment is not certification; live evidence is required for live certification.

---

## 4. Milestone / Workstream Status

| Workstream | Status | Notes |
|---|---|---|
| Initial architecture / provider migration | ✅ Complete | Active provider architecture uses INDMoney / INDstocks; legacy Breeze remains isolated in legacy areas. |
| Instrument master / instrument management | ✅ Complete | Index/equity/F&O masters and strike selection implemented. |
| Live option-chain retrieval | ✅ Complete | Provider integration and canonical option-chain path implemented. |
| Greeks | ✅ Complete | Live/canonical Greeks pipeline implemented. |
| GEX / DEX | ✅ Complete | Exposure analytics implemented. |
| Gamma Wall / Gamma Flip | ✅ Complete | Regime/level analytics implemented. |
| Market Structure | ✅ Complete | Canonical market-structure engine integrated. |
| Expected Move / Max Pain / PCR | ✅ Complete | Canonical fields and fail-closed dashboard semantics covered. |
| OI Flow | ✅ Complete | OI analyzer and decision-intelligence integration covered. |
| Dealer / institutional intelligence | ✅ Complete | Dealer flow/intelligence foundation integrated. |
| Direction-aware scoring | ✅ Complete | Direction preserved through scoring/strategy/decision pipeline. |
| Decision / risk / trade validation | ✅ Complete | Direction and actionability are explicitly separated. |
| Execution lifecycle safety | ✅ Complete | `UNKNOWN` -> reconciliation; retry behavior is explicit. |
| Execution audit / idempotency | ✅ Complete | Append-only audit and durable audit-backed idempotency implemented. |
| Position runtime / restart recovery | ✅ Complete | Restart persistence regression covered. |
| Replay / live isolation | ✅ Complete | Replay cannot create/import live execution state. |
| Dashboard canonical architecture | ✅ Complete | DashboardData + adapters + controller cycle established. |
| Dashboard fail-closed semantics | ✅ Complete | Missing/invalid values do not become fabricated zeroes or stale actionability. |
| Provenance / freshness / integrity | ✅ Complete | Separate freshness/integrity state with explicit degraded/unavailable states. |
| Runtime card / market banner / signal card | ✅ Complete | Contract tests added. |
| Monitoring / health | ✅ Complete | Alert-event and runtime-health infrastructure implemented. |
| Market clock | ✅ Complete | IST/Asia-Kolkata session boundaries and weekend behavior tested. |
| Adaptive Brain | ✅ Complete | Observation, historical similarity/win-rate logic, outcome resolution and restart recovery implemented. |
| Brain SQL persistence | ✅ Implemented/tested | SQL-backed path exists; production database wiring is still pending. |
| Live-cycle evidence | ✅ Implemented/tested | Fail-closed evidence builder and persistence stores implemented. |
| Live validation worker | 🟡 Implemented | Worker wiring exists, but autonomous production execution still needs infrastructure validation. |
| CI / dependency reproducibility | ✅ Complete | Latest GitHub Actions run is green. |
| Real live-market certification | ⚠️ Pending | Genuine live cycles must be captured and independently verified. |
| Autonomous production worker | ⚠️ Pending | Current Render web service uses Streamlit and can sleep when idle. |
| Production PostgreSQL wiring | ⚠️ Pending | Must provision/use a QuantNifty-specific database; do not touch QuantNifty-Next DB. |
| Streamlit UI finalization | ⏸️ Deferred | Explicitly deferred until backend/project completion. |

---

## 5. Latest Regression / CI Evidence

### GitHub Actions

Latest verified run:

- Run: **#86**
- Run ID: `34228980286`
- HEAD: `1c3bbeceffcf883e9afe21a56f33da192f346f27`
- Result: **SUCCESS**
- Dependency installation: PASS
- Python compile check: PASS
- Pytest: PASS

Latest full regression baseline before the live-evidence/infrastructure phase:

- **862 passed**
- **2 skipped**
- **0 known test failures**

The preceding CI failure was dependency-only (`rfc3987-syntax==1.1.1` unavailable). It was corrected to the available `1.1.0` release and the subsequent CI run passed.

---

## 6. Recently Completed Contract / Safety Work

### Dashboard fail-closed semantics

Completed contract coverage includes:

- KPI missing probability/confidence -> `—`; zero remains `0%`.
- Expected Move missing/invalid -> `UNAVAILABLE`; zero preserved.
- Max Pain missing/invalid -> `UNAVAILABLE`; zero preserved.
- PCR missing/invalid -> `UNAVAILABLE`.
- Probability gauge missing/invalid -> unavailable; zero preserved.
- Market banner missing/invalid critical fields -> fail closed.
- Signal card does not infer dealer fields when source data is absent.
- Provenance adapter distinguishes `UNAVAILABLE`, `DEGRADED` and `READY`.
- Runtime card uses canonical runtime/trade/block/position/last-trade state.

### Execution safety

- Adapter timeout/connection failure -> `UNKNOWN` and reconciliation required.
- Mapping/ordinary execution failures -> `FAILED`.
- Lifecycle classification is explicit.
- `UNKNOWN` / `SUBMITTED` -> reconciliation.
- `REJECTED` / `FAILED` / `NOT_SUBMITTED` -> do not retry automatically.
- Execution audit is append-only.
- Repeated lifecycle events for the same client order remain auditable.
- Durable audit-backed idempotency survives restart when durable storage is configured.

### Replay isolation

Regression tests prove replay restores recorded decisions without creating live execution state and does not import live decision/execution attributes from snapshots.

---

## 7. Adaptive Brain Status

The Brain is downstream of the authoritative decision/analytics pipeline and **does not modify the live decision**.

Implemented behavior:

- extracts observations from the canonical runtime context
- stores observations append-only
- resolves WIN/LOSS only from closed trades with numeric P&L
- leaves unresolved outcomes as waiting for outcome
- searches historical resolved observations for similarity
- calculates signal-specific historical win rate when evidence exists
- persists and restores resolved history across restart
- supports SQL-backed persistence when `BRAIN_DATABASE_URL` is configured

Important:

> SQL support is implemented and regression-tested, but production DB wiring is not yet enabled for QuantNifty.

---

## 8. Live Validation Status

Live evidence is represented by a dedicated cycle-evidence model containing, among other fields:

- timestamp
- provider / provider mode
- cycle number
- spot
- option-chain coverage
- option-chain integrity
- runtime status
- trade status
- block reason
- provenance freshness
- Brain status
- learning status
- persistence status
- evidence state

The evidence builder is **fail closed**:

- provider must explicitly identify as a supported live provider
- provider mode must explicitly be `LIVE_PROVIDER`
- missing provider mode is not treated as live
- live certification cannot be inferred from deterministic/replay execution

Historical/local validation logs have previously shown cases such as `Freshness: NOT_VERIFIED` and `Raw Analytics: NOT_VERIFIED`; those are validation failures, not live certification.

### Certification rule

Do **not** mark live validation as PASS merely because:

- code tests pass
- Render deploys
- provider HTTP calls return status 200
- a validation script executes

Live certification requires genuine live provider runtime evidence with verified freshness/integrity and persistence state.

---

## 9. Render / Production Infrastructure Status

### QuantNifty Render service

- Service: `quantnifty-validation`
- Service ID: `srv-daeoeqgu01pc73fc55dg`
- URL: `https://quantnifty-validation.onrender.com`
- Repository: `Sabari2811/QuantNifty`
- Branch: `main`
- Auto deploy: enabled
- Runtime: Python
- Build: `pip install -r requirements.txt`
- Current start command: `streamlit run dashboard/app.py --server.address 0.0.0.0 --server.port $PORT`
- `.python-version`: Python `3.12.14`
- `LIVE_VALIDATION_MODE=true` is configured.
- `APITOKEN` is configured in Render; never paste or expose it in chat.

### Infrastructure limitation

The current service is a Streamlit web service. Render free web services can sleep when idle. Therefore, embedding the validation worker in Streamlit startup does **not** prove continuous/autonomous market-worker execution.

A reliable autonomous worker requires an appropriate production runtime/infrastructure configuration (for example a dedicated worker/cron architecture as appropriate to the deployment plan).

### Database rule

There is an existing Render Postgres resource associated with the separate `quantnifty-next` environment. **Do not attach QuantNifty to that database.**

QuantNifty needs its own explicitly identified production database before claiming durable production persistence.

---

## 10. Remaining Work — Exact Order

### P1 — Verify Brain SQL persistence path

- Reinspect current `brain/sql_store.py` and `brain/adaptive_brain.py`.
- Confirm SQL restart test is present and green.
- Confirm DB failure cannot silently report durable persistence.

### P2 — Verify live evidence persistence path

- Reinspect `monitoring/live_session_evidence.py` and worker wiring.
- Confirm local JSONL is reported as local/ephemeral, not PostgreSQL durability.
- Confirm SQL-backed evidence is only marked durable when DB write succeeds.
- Add/verify restart persistence regression for live evidence.

### P3 — Production readiness/health visibility

Implement a non-secret readiness/health surface that reports configuration state such as:

- live provider configured/not configured
- Brain SQL configured/not configured
- live evidence SQL configured/not configured
- worker mode
- persistence mode
- current runtime state

Never expose credential values.

### P4 — Autonomous worker infrastructure

- Provide a one-cycle worker entry point suitable for production scheduling.
- Ensure one cycle can run without Streamlit.
- Ensure failure/reconciliation semantics are preserved.
- Do not create a second QuantNifty service unless the deployment architecture explicitly requires it.
- Do not touch QuantNifty-Next.

### P5 — Genuine live certification

During market hours:

1. Start the actual live worker.
2. Use configured INDMoney/INDstocks credentials from Render.
3. Capture multiple genuine live cycles.
4. Verify provider mode is `LIVE_PROVIDER`.
5. Verify freshness.
6. Verify option-chain coverage/integrity.
7. Verify raw analytics evidence.
8. Verify decision/intelligence consistency.
9. Verify persistence state.
10. Produce a durable live-session certification report.

Only then change the tracker to **LIVE CERTIFIED**.

### P6 — Streamlit UI

Deferred until the backend/project completion and live-certification infrastructure are sufficiently complete. Do not prioritize UI redesign now.

---

## 11. What Is NOT Pending

Do not reopen these areas without a concrete regression or new requirement:

- provider architecture migration
- core option-chain pipeline
- Greeks/GEX/DEX/Gamma analytics
- direction-aware scoring
- decision/risk separation
- execution UNKNOWN/reconciliation semantics
- append-only execution audit
- restart idempotency foundations
- replay/live isolation
- canonical DashboardData architecture
- dashboard fail-closed semantics
- provenance/freshness/integrity contracts
- Adaptive Brain core behavior
- CI dependency baseline

---

## 12. Current Definition of Done

QuantNifty is considered fully production-ready only when all of the following are true:

- [x] Core backend architecture implemented.
- [x] Canonical decision/risk/execution boundaries enforced.
- [x] Replay isolation regression green.
- [x] Execution lifecycle safety regression green.
- [x] Dashboard contract regression green.
- [x] Brain restart recovery regression green.
- [x] CI green on `main`.
- [x] Live evidence framework implemented.
- [ ] QuantNifty-specific production DB provisioned and wired.
- [ ] Autonomous worker deployed using a runtime that does not depend on an idle-prone Streamlit process.
- [ ] Genuine live cycles captured during market hours.
- [ ] Freshness/integrity/raw-analytics evidence verified from live cycles.
- [ ] Durable live-session certification report produced.
- [ ] Final Streamlit UI validation completed.

---

## 13. Continuation Instructions for a New ChatGPT Session

When a new chat starts:

1. Read this file first.
2. Treat `main` at the latest verified HEAD as authoritative.
3. Inspect the repository before editing.
4. Do not repeat completed architecture work.
5. Start from the first unchecked item in **Section 10 — Remaining Work** unless the user explicitly changes priority.
6. Work implementation-first: inspect → gap → implement → test → commit → deploy → validate.
7. Make one focused change at a time.
8. Run targeted regression after each behavior change.
9. Run full regression before release.
10. Never claim live certification from unit/CI/deployment evidence alone.
11. Never expose `APITOKEN` or other credentials.
12. Never touch `QuantNifty-Next`.
13. Streamlit is deferred unless explicitly reactivated by the user.

### First inspection targets when continuing

Before the next implementation change, inspect the exact current contents of:

- `brain/sql_store.py`
- `brain/adaptive_brain.py`
- `monitoring/live_session_evidence.py`
- `dashboard/live_validation_worker.py`
- `dashboard/app.py`
- `requirements.txt`

Then verify the current tests around Brain SQL persistence, live evidence persistence, worker wiring, and dashboard startup before editing.

---

## 14. Release / Continuation Snapshot

**Software implementation:** ✅ Complete for the current backend scope

**Regression:** ✅ Green

**CI:** ✅ Green

**Production live certification:** ⚠️ Pending

**Autonomous production worker:** ⚠️ Pending

**QuantNifty production DB:** ⚠️ Pending

**Streamlit finalization:** ⏸️ Deferred by user

**Separate QuantNifty-Next project:** 🔒 Untouched / must remain untouched

**Next engineering priority:** production persistence correctness → worker runtime → genuine live evidence → live certification.
