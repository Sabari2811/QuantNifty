# QuantNifty Master Validation Checklist

## R2-011 — Canonical Snapshot / Replay

- [x] Canonical snapshot provenance
- [x] Intelligence artifact persistence
- [x] ReplayLoader intelligence restoration
- [x] Typed replay intelligence contract
- [x] Replay decision equivalence
- [x] Replay intelligence equivalence
- [x] Real recorded snapshot replay equivalence
- [x] Zero-drift real replay gate
- [x] Full regression baseline: 324 passed

## R2-013 — Live Backend Validation / Backend → UI Reconciliation

### Acquisition / Coverage
- [x] Live spot acquisition validated against provider response
- [x] Live option-chain acquisition validated against provider response
- [x] Spot coverage validated
- [x] Option-chain coverage validated across consecutive cycles
- [x] Missing-contract coverage is represented in provenance rather than disappearing from the denominator
- [x] NIFTY expiry selection rejects silent monthly fallback and refreshes stale F&O master
- [x] NIFTY expiry selection validated against the live refreshed instrument master

### Freshness
- [x] Provider candle timestamp is propagated when available
- [x] Provider quote timestamp is preserved by INDMoney normalization when supplied
- [x] Spot provider timestamp is propagated into canonical provenance when supplied
- [x] Option-chain provider timestamp is propagated into canonical provenance when supplied
- [x] Quote freshness is explicitly represented as UNVERIFIED when REST quote payload has no provider timestamp
- [x] Future provider timestamps are rejected from freshness verification
- [x] Consecutive-cycle validation runner added for live provenance/OI checks
- [x] Candle freshness now distinguishes timestamp provenance from actual age
- [x] Historical candle older than the live freshness threshold is STALE rather than VERIFIED
- [x] Timestamp-bearing INDstocks WebSocket price-feed adapter implemented with provider timestamp preservation
- [x] Timestamp-bearing live feed wired into canonical market-data provenance behind explicit live-feed configuration
- [x] Live quote freshness behavior validated with a timestamp-bearing source/session
- [x] Consecutive-cycle freshness behavior validated with timestamp-bearing quotes

### Integrity
- [x] Option-chain integrity validator
- [x] INVALID vs SUSPECT separation
- [x] Integrity reasons preserved in provenance
- [x] Live cycle observed complete coverage with a separate SUSPECT integrity state
- [x] Real live-chain integrity validated during market hours
- [x] Real degraded-data case validated

### OI / Greeks / Analytics
- [x] First live cycle OI baseline validated mechanically
- [x] Deterministic ΔPrice/ΔOI classification validated for all four flow types and NO_CHANGE
- [x] Unmatched current strikes are classified UNKNOWN rather than using a fabricated zero baseline
- [x] Consecutive-cycle OI flow classification validated with known live ΔPrice/ΔOI behavior
- [x] Live Greeks now produce values for the live selected expiry and are covered by regression tests
- [x] Live analytics outputs reconciled against raw provider data for 15 independently checked raw-provider-derived fields (LIVE_RAW_ANALYTICS=PASS)
- [x] Decision/intelligence values reconciled against canonical backend snapshot
- [x] Decision ↔ Intelligence consistency contract implemented
- [x] Decision ↔ Intelligence semantic model distinguishes direction from actionability
- [x] Decision ↔ Intelligence consistency contract validated against fresh live runtime
- [x] Fresh live Decision ↔ Intelligence directional conflict traced to gamma-flip directional misclassification
- [x] Gamma flip retained as GEX regime/level evidence, not converted to BULLISH/BEARISH direction
- [x] IV skew directional mapping retained as an explicit project strategy heuristic because ProbabilityEngine independently uses CALLS_EXPENSIVE → bullish and PUTS_EXPENSIVE → bearish; it is not treated as a standalone directional theorem
- [x] Fresh live Intelligence recommendation=WAIT traced to HistoricalEvidence.recommendation, not to ConvictionEngine, OpportunityQualityEngine, or the structural data-quality gate
- [x] Historical validation recommendation explicitly treated as diagnostic context; it cannot veto an otherwise direction-consistent Decision
- [x] Regression coverage added for BUY PUT + BEARISH Intelligence direction + historical WAIT recommendation

## Backend → UI Reconciliation
- [x] Capture fresh canonical live snapshot
- [x] Add canonical provenance adapter exposing coverage, integrity, freshness, and provider source independently
- [x] Runtime provenance passed from canonical runtime context into dashboard data
- [x] Authoritative live Greeks mapped into option-chain UI by contract identity
- [x] Build backend field inventory for option-chain/provenance fields consumed by UI
- [x] Add a live reconciliation report/runner that consumes one DashboardData cycle and reports backend → UI adapter gaps
- [x] Add deterministic Streamlit AppTest runtime contract for the real dashboard entrypoint; live execution remains a separate evidence gate
- [x] Compare option-chain values field-by-field against a fresh captured UI/runtime snapshot — fresh Streamlit cycle 2026-09-02 19:44–19:45; 11 rows, contract identity unique, UI projection MATCH, no gaps
- [x] Data-quality/provenance fields are mapped independently: coverage, integrity, freshness, source, counts, reasons
- [x] Exact backend integrity contract findings are surfaced in the option-chain UI data-quality details
- [x] Canonical market-summary adapter maps Spot, ATM, PCR, Max Pain, Expected Move, and Expiry from one DashboardData cycle
- [x] Canonical decision adapter maps signal, probabilities, confidence, reasons, and trade-plan signal without recomputation
- [x] Trade Signal UI renders the canonical backend signal instead of recomputing it from probability thresholds
- [x] Compare decision fields field-by-field against a fresh live runtime snapshot — signal, probabilities, confidence, reasons, and trade-plan signal all PASS
- [x] Intelligence adapter maps canonical recommendation, direction, confidence, conviction, opportunity, regime, scenarios, and data-quality states
- [x] Intelligence UI renders those canonical values without recomputation
- [x] Compare intelligence fields field-by-field against a fresh live runtime snapshot — all reported fields PASS; dashboard intelligence status MATCH
- [x] Classify the identified option-chain Greek gap as backend parsing, then fix backend before UI mapping
- [x] Fix backend gaps first for live expiry/Greeks parsing and option-chain coverage denominator
- [x] Fix UI mapping/display gaps second for authoritative Greeks and provenance
- [x] Dashboard header acquisition time uses canonical runtime provenance rather than local render time
- [x] Option-chain UI exposes provider timestamp and verified quote age when backend provenance supplies them
- [x] Validate only affected UI sections with a fresh live provider session — Streamlit UI reconciliation PASS; option chain, decision, intelligence, provenance, and consistency paths all matched
- [ ] Full regression after final live reconciliation

### Test-environment integrity
- [x] Pytest collection does not execute the live INDMoney diagnostic script
- [x] Live-provider failure is not allowed to masquerade as a unit/integration test failure
- [x] WebSocket environment variables cannot activate live networking for non-INDMoney test doubles
- [x] Missing WebSocket index-token configuration fails closed for real INDMoney live-feed activation

## UI Validation
- [x] Live option-chain strike ordering
- [x] Highlighted-row readability
- [x] Compact AI decision reasons
- [x] Compact execution plan
- [x] Unnecessary AI section removal
- [x] Provenance/integrity UI separation
- [x] Exact backend integrity findings are available in the option-chain data-quality details
- [x] Decision UI no longer derives its displayed signal from probability thresholds
- [x] Intelligence UI is sourced from the canonical intelligence adapter
- [x] Provider timestamp and quote age are displayed when available from canonical provenance
- [x] Freshness state matches backend in a fresh running UI session — backend and UI both UNVERIFIED; provider quote timestamp unavailable and WebSocket receive timed out
- [x] Coverage state matches backend in a fresh running UI session — backend/UI both COMPLETE at 22/22 option contracts and 100% coverage
- [x] Integrity state matches backend in a fresh running UI session — backend/UI both VALID for option-chain provenance
- [x] Live degraded-data presentation validated at runtime boundary (analytics/trading blocked; UI rendering still pending)
- [x] Decision ↔ Intelligence conflict/deferred state is surfaced clearly in the UI path and covered by regression assertions

## Release Gate
- [x] Fresh live-session backend validation complete — fresh INDMoney-backed Streamlit cycle completed; coverage/integrity and backend→UI mappings reconciled with no gaps
- [x] Backend → UI single-cycle reconciliation complete
- [x] Decision ↔ Intelligence semantic reconciliation validated against fresh live runtime
- [x] Targeted tests pass for previously implemented R2-013 fixes
- [x] Real snapshot replay gate passes
- [ ] Full regression after final live reconciliation
- [ ] Master checklist fully green for R2-013

### Fresh live evidence note

Fresh Streamlit UI validation on 2026-09-02 completed with `STREAMLIT_UI_RECONCILIATION=PASS`. The live cycle reported `dashboard_ui_runtime.status=PASS`, `option_chain.ui_projection.status=MATCH`, `provenance.status=PASS`, `decision_intelligence.status=MATCH`, and `gaps=[]`. The selected expiry was `09/08/2026 14:00`, with 11 strikes / 22 option contracts and 22/22 quotes received. Decision was `WAIT`; Intelligence recommendation was `WAIT` with `BEARISH` direction; consistency was `CONSISTENT`, `actionable=false`, `vetoed=false`.

This post-market REST-backed run does **not** provide fresh timestamp-bearing quote evidence: option quote provenance remained `FRESHNESS_UNVERIFIED` because the provider quote timestamp was unavailable and the WebSocket quote receive timed out. Historical candles were explicitly `STALE` with provider timestamp `2026-09-02 09:55:00+00:00` and measured age `15632.943953s`. Therefore the previously established timestamp-bearing WebSocket freshness gates remain unchanged; no false freshness-green status is claimed from this run.
