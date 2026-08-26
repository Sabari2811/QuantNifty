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
- [x] Full regression baseline: 321 passed

## R2-013 — Live Backend Validation / Backend → UI Reconciliation

### Acquisition / Coverage

- [x] Live spot acquisition validated against provider response
- [ ] Live option-chain acquisition validated against provider response
- [x] Spot coverage validated
- [ ] Option-chain coverage validated across consecutive cycles
- [x] Missing-contract coverage is represented in provenance rather than disappearing from the denominator
- [x] NIFTY expiry selection rejects silent monthly fallback and refreshes stale F&O master
- [ ] NIFTY expiry selection validated against the live refreshed instrument master

### Freshness

- [x] Provider candle timestamp is propagated when available
- [x] Quote freshness is explicitly represented as UNVERIFIED when REST quote payload has no provider timestamp
- [ ] Live quote freshness behavior validated with a timestamp-bearing source/session
- [ ] Consecutive-cycle freshness behavior validated

### Integrity

- [x] Option-chain integrity validator
- [x] INVALID vs SUSPECT separation
- [x] Integrity reasons preserved in provenance
- [x] Live cycle observed complete coverage with a separate SUSPECT integrity state
- [ ] Real live-chain integrity validated during market hours
- [ ] Real degraded-data case validated

### OI / Greeks / Analytics

- [ ] First live cycle OI baseline validated
- [ ] Consecutive-cycle OI flow validated
- [x] Live Greeks now produce values for the live selected expiry and are covered by regression tests
- [ ] Live analytics outputs reconciled against raw provider data
- [ ] Decision/intelligence values reconciled against canonical backend snapshot
- [x] Decision ↔ Intelligence consistency contract implemented
- [ ] Decision ↔ Intelligence consistency contract validated against fresh live runtime

## Backend → UI Reconciliation

- [ ] Capture fresh canonical live snapshot
- [x] Add canonical provenance adapter exposing coverage, integrity, freshness, and provider source independently
- [x] Runtime provenance passed from canonical runtime context into dashboard data
- [x] Authoritative live Greeks mapped into option-chain UI by contract identity
- [x] Build backend field inventory for option-chain/provenance fields consumed by UI
- [x] Add a live reconciliation report/runner that consumes one DashboardData cycle and reports backend → UI adapter gaps
- [ ] Compare option-chain values field-by-field against a fresh captured UI/runtime snapshot
- [x] Data-quality/provenance fields are mapped independently: coverage, integrity, freshness, source, counts, reasons
- [x] Exact backend integrity contract findings are surfaced in the option-chain UI data-quality details
- [x] Canonical market-summary adapter maps Spot, ATM, PCR, Max Pain, Expected Move, and Expiry from one DashboardData cycle
- [x] Canonical decision adapter maps signal, probabilities, confidence, reasons, and trade-plan signal without recomputation
- [x] Trade Signal UI renders the canonical backend signal instead of recomputing it from probability thresholds
- [ ] Compare decision fields field-by-field against a fresh live runtime snapshot
- [x] Intelligence adapter maps canonical recommendation, direction, confidence, conviction, opportunity, regime, scenarios, and data-quality states
- [x] Intelligence UI renders those canonical values without recomputation
- [ ] Compare intelligence fields field-by-field against a fresh live runtime snapshot
- [x] Classify the identified option-chain Greek gap as backend parsing, then fix backend before UI mapping
- [x] Fix backend gaps first for live expiry/Greeks parsing and option-chain coverage denominator
- [x] Fix UI mapping/display gaps second for authoritative Greeks and provenance
- [x] Dashboard header acquisition time uses canonical runtime provenance rather than local render time
- [ ] Validate only affected UI sections with a fresh live provider session
- [ ] Full regression after final live reconciliation

### Test-environment integrity

- [x] Pytest collection does not execute the live INDMoney diagnostic script
- [x] Live-provider failure is not allowed to masquerade as a unit/integration test failure

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
- [ ] Freshness state matches backend in a fresh running UI session
- [ ] Coverage state matches backend in a fresh running UI session
- [ ] Integrity state matches backend in a fresh running UI session
- [ ] Live degraded-data presentation validated
- [ ] Decision ↔ Intelligence conflict state is surfaced clearly in the UI

## Release Gate

- [ ] Fresh live-session backend validation complete
- [ ] Backend → UI reconciliation complete
- [ ] Decision ↔ Intelligence semantic reconciliation validated
- [x] Targeted tests pass for previously implemented R2-013 fixes
- [x] Real snapshot replay gate passes
- [ ] Full regression after final live reconciliation
- [ ] Master checklist fully green for R2-013
