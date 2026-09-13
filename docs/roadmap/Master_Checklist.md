# QuantNifty — Master Progress & Continuation Tracker

**Last updated:** 2026-09-13
**Repository:** `Sabari2811/QuantNifty`
**Authoritative branch:** `main`
**Current verified HEAD:** `86c729e043c368e5b04b027e11ade178e3889b04`
**Current state:** NIFTY decision/trade cockpit and execution-policy hardening deployed; live certification remains evidence-gated.

> This is the primary continuation tracker. Read it before starting new work. Continue from the current `main` state; do not restart completed architecture work unless new evidence requires it.

---

## 1. Project Summary

QuantNifty is a NIFTY-specific options market-intelligence, decision, paper-trading, replay/backtesting, learning, monitoring and dashboard platform.

Canonical chain:

```text
Live NIFTY Market Data
        ↓
Market / Option Analytics
        ↓
Direction-aware Signal
        ↓
Authoritative NIFTY Decision
        ↓
Brain / Learning Gate
        ↓
Risk Gate
        ↓
Execution Intent
        ↓
Paper / Broker Execution
        ↓
Position / Trade Lifecycle
        ↓
P&L / Performance
        ↓
Learning Observation
        ↓
Dashboard / Audit Evidence
```

The system is intentionally NIFTY-specific rather than a generic multi-index engine.

---

## 2. Repository Rules

- Repository: `Sabari2811/QuantNifty`
- Branch: **`main`**
- Never modify `Sabari2811/QuantNifty-Next`.
- Never expose or commit credentials, API tokens, database URLs or other secrets.
- Existing Render services must be reused; do not create duplicate services.
- Workflow: **Inspect → identify gap → implement → test → commit → deploy → validate → report**.

---

## 3. Latest Git State

Current HEAD:

```text
86c729e043c368e5b04b027e11ade178e3889b04
```

Latest commit:

```text
test: lock explicit NIFTY cutoff semantics
```

Recent relevant commits:

```text
86c729e  test: lock explicit NIFTY cutoff semantics
9d5bc7e  refactor: make NIFTY entry and force-exit cutoffs explicit
58d73d1  fix: keep live monitor only in NIFTY cockpit
7fc08de  test: enforce cockpit-only live monitor placement
```

The latest GitHub Actions regression observed for `86c729e` completed successfully.

---

## 4. NIFTY Trading Policy

The active trading architecture enforces/intends:

- Symbol: `NIFTY`
- Options: CE / PE only
- Direction comes from the canonical NIFTY signal.
- Scoring must not invent or reverse direction.
- Delta validation is required for selected option contracts.
- Maximum daily underlying movement: **400 points**
- Maximum trade movement: **250 points**
- Risk movement model: **100 points**
- Target-1 movement model: **150 points**
- Target-2 movement model: **250 points**
- Maximum trades/day: **3**
- Maximum simultaneous position: **1**
- Entry cutoff: **15:35 IST**
- Overnight position: disabled
- Force-close at the intraday cutoff
- Risk/data/authentication/reconciliation failures fail closed

---

## 5. Workstream Status

| Workstream | Status | Current evidence / note |
|---|---|---|
| Provider migration | ✅ Complete | Active provider architecture uses INDMoney / INDstocks; legacy Breeze isolated. |
| Instrument master / strike selection | ✅ Complete | Index/equity/F&O masters and NIFTY strike selection implemented. |
| Live option-chain retrieval | ✅ Complete | Canonical provider option-chain path implemented. |
| Greeks / GEX / DEX | ✅ Complete | Canonical exposure/Greeks pipeline implemented. |
| Gamma Wall / Gamma Flip | ✅ Complete | Used as regime/level evidence, not standalone signal. |
| Market Structure | ✅ Complete | Canonical market-structure engine integrated. |
| Expected Move / Max Pain / PCR | ✅ Complete | Canonical fields and fail-closed UI semantics covered. |
| OI Flow / Dealer intelligence | ✅ Complete | Decision-intelligence inputs integrated. |
| Direction-aware scoring | ✅ Complete | Authoritative direction preserved through scoring/strategy/decision. |
| Decision / risk / trade validation | ✅ Complete | Direction and actionability separated. |
| NIFTY execution policy | ✅ Complete | Entry/force-exit cutoff semantics explicitly enforced and regression-tested. |
| Execution lifecycle safety | ✅ Complete | UNKNOWN requires reconciliation; retry semantics explicit. |
| Execution audit / idempotency | ✅ Complete | Append-only audit and durable idempotency foundations implemented. |
| Position restart recovery | ✅ Complete | Recovery/reconciliation boundary regression covered. |
| Replay / live isolation | ✅ Complete | Replay cannot create/import live execution state. |
| Adaptive Brain | ✅ Implemented/tested | Similarity, outcome resolution, learning and restart recovery implemented; live production evidence still pending. |
| Live-cycle evidence | ✅ Implemented/tested | Fail-closed evidence model and stores implemented. |
| Live certification verifier | ✅ Implemented/tested | Requires genuine live identity, freshness/integrity and durable persistence. |
| After-market validation | ✅ Implemented/tested | Backtest, strategy contract, temporal integrity, leakage, walk-forward and robustness orchestration available. |
| Backtest metrics/gates | ✅ Implemented/tested | P&L, win rate, profit factor, expectancy, drawdown and loss-streak gates. |
| Dashboard canonical architecture | ✅ Complete | DashboardData + controller + read-only presentation mapping. |
| NIFTY Trade Cockpit | ✅ Implemented/deployed | Primary one-screen NIFTY decision/trade view. |
| Live Trade Monitor | ✅ Implemented/deployed | Owned only by NIFTY cockpit; provider-observed option LTP/P&L refresh. |
| Full Terminal duplication cleanup | ✅ Complete | Live monitor removed from Full Terminal; detailed analytics retained. |
| Backend ↔ UI integrity | ✅ Implemented/tested | Canonical UI contract and integrity checks retained. |
| CI regression | ✅ Green | Latest observed run for `86c729e` succeeded. |
| Render UI deployment | ✅ Live | `quantnifty-validation` deployed from `main`; latest observed deployment for `86c729e` is live. |
| Production PostgreSQL wiring | 🟡 Wired / verify | QuantNifty-specific DB wiring exists; genuine-cycle persistence/restart verification remains. |
| WebSocket live feed | ⚠️ Not certified | REST quote path works where authenticated; WebSocket requires successful authenticated handshake + real tick evidence before certification. |
| Genuine live-market certification | ⚠️ Pending | Requires multiple independently verified live cycles. |
| Historical strategy acceptance | ⚠️ Pending | Requires real machine-readable historical NIFTY option data and explicit acceptance thresholds. |
| Final E2E certification | ⚠️ Pending | Depends on live evidence + historical validation + durable persistence evidence. |

---

## 6. Current UI Architecture

Primary tab:

### 🎯 NIFTY Trade Cockpit

Contains the decision-critical single-screen view:

- NIFTY spot
- signal / confidence / regime
- support / resistance
- liquidity support/resistance
- call/put walls
- gamma flip / gamma wall
- dealer gamma / dealer flow
- PCR / Max Pain / market structure
- expected move and probabilities
- action / CE-PE / strike / entry / SL / targets
- risk/reward / risk state
- Brain status
- trade status / block reason
- **Live Trade Monitor**

The Live Trade Monitor refreshes only current provider quote/P&L state; it does not rerun the decision engine every few seconds and therefore does not create duplicate decisions/trades.

Secondary tab:

### 📊 Full Terminal

Retains the detailed analytics, option chain, Greeks, heatmaps, execution state, Brain/paper performance, integrity report and analytics output.

The live monitor is intentionally **not** rendered here to avoid visual duplication.

---

## 7. Brain / Learning Rules

The Brain is an evidence-based downstream learning layer.

- Uses canonical NIFTY setup fingerprints.
- Learns from resolved trade outcomes, not arbitrary historical research leakage.
- Requires sufficient similar resolved setups before a historical profitability gate can affect actionability.
- Can PASS or VETO an otherwise valid trade to WAIT; it must not reverse BUY_CALL into BUY_PUT.
- Outcome resolution is tied to the original trade/entry identity.
- Resolved observations are idempotent.
- Restart recovery restores resolved learning history when the configured durable store is available.
- Adaptive mutation remains disabled during validation.

Production Brain/PostgreSQL behavior is not considered certified until a genuine production observation and restart/read-back are evidenced.

---

## 8. Live Validation Rules

Do not mark live validation PASS merely because:

- unit/regression tests pass
- Render deployment succeeds
- an HTTP provider request returns 200
- a validation script runs

Genuine live certification requires:

1. supported live provider identity
2. `LIVE_PROVIDER` mode
3. fresh provider data
4. valid option-chain coverage/integrity
5. raw analytics evidence
6. decision/intelligence consistency
7. Brain/evidence persistence
8. multiple valid cycles
9. independent fail-closed certification verification

Deployment, test completion, live validation and production certification are separate states.

---

## 9. Render Status

Existing QuantNifty services remain the deployment boundary.

- Streamlit UI: `quantnifty-validation`
- Live validation worker service: `quantnifty-live-validation-worker`
- QuantNifty-specific Postgres: `quantnifty-production`
- Current UI deployment from `86c729e` is **live**.
- The worker architecture remains a foreground web-service workaround; native background-worker conversion is optional infrastructure work, not a strategy-code blocker.

Never use the separate `QuantNifty-Next` infrastructure.

---

## 10. Current Priority Queue

### P0 — Live provider/runtime correctness

- Confirm current INDstocks authentication in production runtime.
- Confirm genuine option-chain freshness/integrity.
- Confirm live provider identity and cycle evidence.
- Confirm WebSocket only if a real authenticated handshake and timestamped ticks are observed.

### P1 — Durable live validation

- Capture multiple genuine NIFTY cycles during market hours.
- Verify Brain/evidence PostgreSQL writes.
- Restart the worker and verify durable read-back.
- Run the fail-closed live certification verifier.

### P2 — Historical strategy validation

- Obtain an accepted machine-readable historical NIFTY option dataset.
- Run chronological replay/backtest.
- Evaluate P&L, expectancy, drawdown, trade frequency, leakage, walk-forward and regime robustness.
- Do not invent historical performance from synthetic fixtures.

### P3 — Final certification

Combine software regression, replay isolation, execution safety, historical results, walk-forward/out-of-sample evidence, robustness, genuine live evidence and durable persistence.

### P4 — Further strategy refinement

Only after the gates above are green:

- false-breakout filtering
- entry timing
- strike selection
- setup matching
- trade attribution
- profitable-scenario preference

Do not add strategy complexity before core data/decision/risk/execution contracts are proven.

---

## 11. What Is NOT Pending

Do not reopen these without a concrete regression or new requirement:

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
- Adaptive Brain core implementation
- live evidence implementation
- live certification verifier implementation
- after-market validation framework implementation
- NIFTY cockpit/live-monitor architecture
- removal of duplicate live-monitor presentation

---

## 12. Definition of Done

### Engineering

- [x] Core backend architecture implemented.
- [x] Canonical decision/risk/execution boundaries enforced.
- [x] Replay isolation regression green.
- [x] Execution lifecycle safety regression green.
- [x] Dashboard contract regression green.
- [x] Brain restart recovery regression green.
- [x] Live evidence framework implemented.
- [x] After-market/backtest validation framework implemented.
- [x] Walk-forward/leakage/robustness framework implemented.
- [x] Fail-closed live certification verifier implemented.
- [x] NIFTY-specific execution cutoff semantics regression-tested.
- [x] Primary NIFTY Trade Cockpit deployed.
- [x] Live monitor consolidated into cockpit only.
- [x] Latest observed GitHub regression for `86c729e` green.

### Still gated

- [ ] Genuine live cycles captured and independently verified.
- [ ] Freshness/integrity/raw analytics verified from live cycles.
- [ ] Brain/evidence persistence verified across genuine production restart.
- [ ] WebSocket authenticated handshake and real tick evidence, if WebSocket is used for certification.
- [ ] Historical NIFTY option dataset accepted and decoded.
- [ ] Historical strategy acceptance thresholds evaluated from real data.
- [ ] Walk-forward/out-of-sample results accepted.
- [ ] Robustness/regime results accepted.
- [ ] Durable live-session certification report produced.
- [ ] Final end-to-end production certification.

---

## 13. Continuation Instructions

When continuing QuantNifty in a new session:

1. Read this tracker first.
2. Inspect `Sabari2811/QuantNifty` on `main` before making claims.
3. Never touch `QuantNifty-Next`.
4. Compare current repository state with this tracker and recent commits.
5. Identify the highest-priority concrete blocker/gap.
6. Implement the smallest safe change automatically when the next step is clear.
7. Add targeted regression coverage.
8. Run targeted tests and full regression before release.
9. Let existing Render auto-deployment handle `main` changes where configured.
10. Validate GitHub, CI, Render, runtime, data, decision, execution, persistence and UI evidence separately.
11. Update this tracker after meaningful progress with the latest commit, project state, completed work, remaining gates and evidence.
12. Never claim live certification without genuine live evidence.

**Final principle:** correctness, evidence, risk control, canonical ownership and incremental learning take priority over feature count.
