# QuantNifty Project Roadmap

## Current Baseline

- Git commit: `696b535`
- Git tag: `R2-003-green`
- Regression: `65 passed`
- Failures: `0`
- Collection errors: `0`
- Warnings: `1`
- Current warning: `py_vollib` deprecation

## Phase 0 — Core Backend

- [x] Project architecture
- [x] Provider abstraction
- [x] INDMoney provider
- [x] Instrument Manager
- [x] Runtime configuration
- [x] Runtime Manager
- [x] Replay infrastructure
- [x] Paper broker
- [x] Backtest foundation

## Phase 1 — Analytics

- [x] Greeks
- [x] Gamma Exposure
- [x] Delta Exposure
- [x] Gamma Wall
- [x] Gamma Flip
- [x] Dealer Flow
- [x] Liquidity
- [x] Market Structure
- [x] PCR
- [x] OI Flow
- [x] IV Skew
- [x] Expected Move
- [x] ATR / Volatility
- [x] Prediction
- [x] Institutional scoring
- [ ] Advanced analytics refinement

## Phase 2 — Decision Intelligence

- [x] Direction-aware scoring
- [x] Direction quality separation
- [x] Directional adapters
- [x] Directional snapshot handling
- [x] Strategy direction preservation
- [x] Authoritative DecisionBuilder direction
- [x] DecisionEngine runtime direction
- [x] Premium trade generation
- [x] Risk calculations
- [x] Trade validation
- [x] Execution planning

## Phase 3 — Regression / Hardening

- [x] Full pytest collection
- [x] Backtest regression
- [x] Decision pipeline regression
- [x] Gamma Flip import correction
- [x] OI Engine regression
- [x] Session Manager test isolation
- [x] Direction-aware regression
- [x] 65/65 full regression
- [ ] Remove py_vollib deprecation warning
- [ ] Add Gamma Flip unit-test coverage
- [ ] Additional integration tests
- [ ] Performance tests

## Phase 4 — Quant Validation

- [ ] Historical dataset preparation
- [ ] Replay-based backtesting
- [ ] Strategy backtesting
- [ ] CALL vs PUT analysis
- [ ] Market-regime analysis
- [ ] Parameter robustness
- [ ] Walk-forward testing
- [ ] Monte Carlo / statistical validation
- [ ] Performance report

## Phase 5 — UI / Dashboard

- [ ] Dashboard consolidation
- [ ] Market Intelligence
- [ ] Dealer Intelligence
- [ ] OI / Gamma visualization
- [ ] Direction-aware signal panel
- [ ] Trade execution panel
- [ ] Replay Workbench
- [ ] Runtime Monitor
- [ ] Backtest Research UI
- [ ] Portfolio Intelligence

## Phase 6 — Alerts

- [ ] Telegram integration
- [ ] Signal alerts
- [ ] Trade alerts
- [ ] Risk alerts
- [ ] System alerts

## Phase 7 — Production

- [ ] Production monitoring
- [ ] Provider failover
- [ ] Risk controls
- [ ] Kill switch
- [ ] Paper-trading soak test
- [ ] Production readiness review
- [ ] Live deployment

## Current Next Milestone

R2-004 — Greeks dependency audit and deprecation cleanup.
