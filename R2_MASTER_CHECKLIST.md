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
- [x] Full regression baseline: 299 passed

## R2-013 — Live Backend Validation / Backend → UI Reconciliation

### Acquisition / Coverage

- [x] Live spot acquisition validated against provider response
- [ ] Live option-chain acquisition validated against provider response
- [x] Spot coverage validated
- [ ] Option-chain coverage validated across consecutive cycles
- [ ] Missing-contract behavior validated
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
- [ ] Live Greeks inputs validated
- [ ] Live analytics outputs reconciled against raw provider data
- [ ] Decision/intelligence values reconciled against canonical backend snapshot

## Backend → UI Reconciliation

- [ ] Capture fresh canonical live snapshot
- [ ] Build backend field inventory consumed by UI
- [ ] Compare option-chain values field-by-field
- [ ] Compare data-quality/provenance fields field-by-field
- [ ] Compare decision fields field-by-field
- [ ] Compare intelligence fields field-by-field
- [ ] Classify each gap as backend, mapping, formatting, or UI-only
- [ ] Fix backend gaps first
- [ ] Fix UI mapping/display gaps second
- [ ] Validate only affected UI sections
- [ ] Full regression after reconciliation

## UI Validation

- [x] Live option-chain strike ordering
- [x] Highlighted-row readability
- [x] Compact AI decision reasons
- [x] Compact execution plan
- [x] Unnecessary AI section removed
- [x] Provenance/integrity UI separation
- [ ] Freshness state matches backend
- [ ] Coverage state matches backend
- [ ] Integrity state matches backend
- [ ] Live degraded-data presentation validated

## Release Gate

- [ ] Fresh live-session backend validation complete
- [ ] Backend → UI reconciliation complete
- [ ] Targeted tests pass
- [ ] Real snapshot replay gate passes
- [ ] Full regression passes
- [ ] Master checklist fully green for R2-013
