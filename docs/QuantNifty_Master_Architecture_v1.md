# QuantNifty Master Architecture v1

## 1. System Purpose

QuantNifty is a modular NIFTY options analytics, decision, execution, replay and backtesting platform.

The architecture is designed around:

- Provider independence
- Modular analytics
- Direction-aware decision intelligence
- Backend-authoritative trading logic
- Replay and backtesting
- Paper trading
- Production risk controls
- UI/backend contract separation

---

# 2. High-Level Architecture

```text
                    MARKET / BROKER DATA
                            |
                            v
                    +---------------+
                    |   PROVIDER    |
                    +---------------+
                            |
                            v
              +---------------------------+
              | Instrument / Market Data  |
              +---------------------------+
                            |
                            v
                    +---------------+
                    |   ANALYTICS   |
                    +---------------+
                            |
          +-----------------+------------------+
          |                 |                  |
          v                 v                  v
      Market State      Options Flow      Intelligence
      Structure         OI / PCR          GEX / DEX
      Liquidity         IV / Skew         Dealer Flow
      Volatility        Expected Move     Prediction
          |                 |                  |
          +-----------------+------------------+
                            |
                            v
                  +---------------------+
                  |  MARKET ANALYZER    |
                  +---------------------+
                            |
                            v
                  +---------------------+
                  | DIRECTION-AWARE     |
                  | SCORING ENGINE      |
                  +---------------------+
                            |
                            v
                  +---------------------+
                  | STRATEGY SELECTOR   |
                  +---------------------+
                            |
                            v
                  +---------------------+
                  | DECISION BUILDER    |
                  +---------------------+
                            |
                            v
                  +---------------------+
                  | EXECUTION PLANNING  |
                  +---------------------+
                            |
                            v
                  +---------------------+
                  | TRADE VALIDATOR     |
                  +---------------------+
                            |
             +--------------+--------------+
             |              |              |
             v              v              v
        PAPER TRADE      REPLAY        BACKTEST
             |              |              |
             +--------------+--------------+
                            |
                            v
                    PERFORMANCE DATA
                            |
                            v
                           UI
```

---

# 3. Provider Layer

The provider layer isolates external broker/data-provider implementations from the rest of QuantNifty.

## Active Provider

INDMoney / INDstocks is the active provider architecture.

## Legacy

ICICI Breeze-related code exists in legacy areas.

Legacy provider code must not become a dependency of the active QuantNifty pipeline.

## Responsibilities

- Authentication
- Instrument data
- Market data
- Option-chain data
- Order interfaces
- Provider session handling
- Provider-specific error handling

The rest of the system should consume normalized internal contracts rather than provider-specific structures.

---

# 4. Instrument / Market Data Layer

Responsibilities:

- Instrument master
- Index instruments
- Equity instruments
- Futures
- Options
- Strike lookup
- Expiry lookup
- Contract metadata
- Provider-to-internal normalization

The Instrument Manager acts as the abstraction between provider instrument data and downstream analytics.

---

# 5. Analytics Layer

Analytics converts raw market information into structured intelligence.

## Market Analytics

- Market structure
- Trend
- Range
- Support / resistance
- VWAP
- CPR
- Camarilla
- Liquidity
- ATR
- Volatility
- Expected Move

## Options Analytics

- Greeks
- Implied volatility
- IV Skew
- Open Interest
- OI Flow
- PCR
- Max Pain

## Dealer / Exposure Analytics

- Gamma Exposure
- Delta Exposure
- Gamma Wall
- Gamma Flip
- Call Wall
- Put Wall
- Dealer Flow
- Dealer positioning

## Prediction / Intelligence

- Probability
- Institutional state
- Market intelligence
- Signal intelligence
- Feature engineering

Analytics must remain independently testable.

---

# 6. Market Snapshot

The MarketSnapshot is the primary internal market-state contract consumed by downstream decision components.

It can contain structured state such as:

- Spot
- Greeks
- Dealer data
- Institutional data
- Prediction
- PCR
- Expected Move
- ATR
- Market structure
- Signal
- Direction
- Confidence

The snapshot is the boundary between market analytics and decision intelligence.

---

# 7. Market Analysis

MarketAnalyzer converts the MarketSnapshot into a normalized MarketContext.

MarketContext represents the decision-ready state of the market.

Typical dimensions include:

- Regime
- Bias
- Dealer state
- Gamma state
- Volatility
- ATR
- Expected Move
- PCR bias
- Institutional state
- Liquidity
- Probability
- Gamma Flip
- Gamma Wall
- Call Wall
- Put Wall
- Max Pain

---

# 8. Direction-Aware Decision Intelligence

Direction is an explicit part of the decision pipeline.

The architecture must distinguish:

```text
BUY CALL
BUY PUT
WAIT
```

from merely having a positive or negative numerical score.

## Direction Rules

Positive score does not automatically mean CALL.

Negative score does not automatically mean PUT.

The authoritative direction may originate from the market snapshot / upstream directional analysis.

The decision pipeline must preserve that direction.

## Components

- Directional Score Adapter
- Directional Snapshot Adapter
- Scoring Engine
- Strategy Selector
- Decision Builder
- Decision Engine

---

# 9. Scoring Engine

The scoring engine evaluates market quality.

It produces:

- Quality score
- Signed score
- Score breakdown
- Reasons
- Direction

The architecture separates:

```text
QUALITY
```

from:

```text
DIRECTION
```

This prevents a strong PUT setup from being converted into a CALL merely because of score polarity.

---

# 10. Strategy Layer

StrategySelector selects the appropriate strategy according to market context.

Examples:

- TrendStrategy
- RangeStrategy

Strategies may adjust score quality or strategy-specific factors, but they must preserve the authoritative trade direction.

Direction preservation is regression-tested.

---

# 11. Decision Builder

DecisionBuilder converts the analyzed/scored state into a decision.

The decision contains:

- Signal
- Direction
- Score
- Score breakdown
- Reasons
- Validity
- Decision metadata

The authoritative direction must not be silently replaced by legacy score-sign logic when an explicit direction is available.

Legacy score-only behavior remains available where required for backward compatibility.

---

# 12. Decision Engine

DecisionEngine orchestrates:

```text
Market Snapshot
       |
       v
Market Analyzer
       |
       v
Scoring Engine
       |
       v
Strategy Selector
       |
       v
Decision Builder
       |
       v
Execution Engine
```

The DecisionEngine is an orchestration layer.

Business rules should remain inside their respective components.

---

# 13. Execution Layer

Execution converts a valid decision into a trade plan.

Responsibilities include:

- Option type
- Strike selection
- Entry
- Stop loss
- Targets
- Risk/reward
- Lot size
- Number of lots
- Capital allocation
- Trade quality

The execution layer must consume the decision rather than independently reconstructing market direction.

---

# 14. Trade Validation

TradeValidator is the final quality/risk boundary before a trade becomes executable.

Validation considers factors such as:

- Risk/reward
- Trade quality
- Risk constraints
- Execution feasibility
- Required trade conditions

An invalid trade may result in:

```text
WAIT
```

even when the upstream decision has a directional signal.

This distinction is intentional:

```text
Decision Signal != Executable Trade
```

---

# 15. Replay Architecture

Replay allows historical market states to pass through the same decision pipeline used by live analysis.

```text
Historical Data
      |
      v
Replay Engine
      |
      v
Market Snapshot
      |
      v
Analytics
      |
      v
Decision Engine
      |
      v
Execution / Paper Broker
      |
      v
Performance
```

Replay should avoid creating a separate set of trading rules.

---

# 16. Backtesting

Backtesting evaluates the strategy against historical/replayed market states.

Required metrics include:

- Total trades
- Winning trades
- Losing trades
- Win rate
- Profit factor
- Expectancy
- Average R
- Maximum drawdown
- Sharpe
- CALL performance
- PUT performance
- Regime performance
- Time-of-day performance

Backtesting must use the same authoritative decision contracts wherever possible.

---

# 17. Paper Trading

Paper trading provides a controlled bridge between backtesting and live execution.

Paper trading must preserve:

- Direction
- Strike
- Entry
- Stop
- Targets
- Position size
- Risk
- Validation

It must also maintain an audit trail.

---

# 18. UI Architecture

The UI is a first-class QuantNifty component.

The UI consumes backend contracts.

The UI must not recreate:

- Scoring
- Direction
- Strike selection
- Risk calculations
- Validation
- Execution rules

## Major UI Areas

### Dashboard

- Market state
- Spot
- Regime
- Provider status
- Data freshness

### Market Intelligence

- Structure
- VWAP
- CPR
- Liquidity
- Expected Move
- ATR
- Volatility

### Dealer Intelligence

- GEX
- DEX
- Gamma Flip
- Gamma Wall
- Call Wall
- Put Wall
- OI
- PCR
- IV Skew

### Decision Intelligence

- Direction
- Quality
- Confidence
- Score breakdown
- Reasons
- Validation

### Trade Panel

- Contract
- Entry
- Stop
- Targets
- Lots
- Risk/reward
- Trade quality

### Replay / Backtest

- Historical date
- Replay controls
- Signal timeline
- Trade timeline
- P&L
- Drawdown

### Runtime

- Provider status
- Data freshness
- Analytics status
- Decision status
- Execution status
- Errors

---

# 19. Backend / UI Contract

The backend is authoritative.

```text
Backend State
      |
      v
API / WebSocket Contract
      |
      v
UI
```

The UI displays the backend state.

It does not independently calculate trading decisions.

This prevents:

- Backend/UI disagreement
- Different score calculations
- Different direction calculations
- Different risk calculations
- Different validation results

---

# 20. Risk Architecture

Risk controls must exist independently of the UI.

Required controls:

- Maximum daily loss
- Maximum trade risk
- Maximum lots
- Maximum trades
- Maximum position size
- Kill switch
- Paper/live mode
- Broker availability
- Execution validation

Risk controls must remain enforceable even if the UI is unavailable.

---

# 21. Runtime Architecture

Runtime monitoring should expose:

- Provider health
- API latency
- Data freshness
- Analytics health
- Decision Engine health
- Execution health
- Error state
- Alert state

The runtime layer should provide observability without owning trading logic.

---

# 22. Testing Architecture

Testing is divided into:

## Unit Tests

Individual components.

## Contract Tests

Validate interfaces between components.

## Direction Tests

Validate:

- BUY CALL preservation
- BUY PUT preservation
- WAIT preservation
- Quality/direction separation

## Integration Tests

Validate the complete decision pipeline.

## Runtime Tests

Validate live-style decision execution.

## Backtest Tests

Validate replay/backtest integration.

## Full Regression

The R2-003 baseline is:

    65 passed
    0 failures
    0 collection errors
    1 warning

---

# 23. Current Git Baseline

Commit:

    696b535

Tag:

    R2-003-green

Release:

    R2-003

Description:

    Direction-aware regression stabilization

---

# 24. Current Known Warning

The only current full-suite warning is:

`py_vollib` deprecation.

This is intentionally deferred to R2-004.

The migration must first be audited for:

- API compatibility
- Numerical compatibility
- Implied-volatility behavior
- Greeks behavior
- Regression impact

No dependency replacement should be performed blindly.

---

# 25. Development Governance

Major milestones should produce:

1. Code changes
2. Tests
3. Full regression
4. Git commit
5. Git tag where appropriate
6. Release documentation

The project should maintain known-good rollback points.

R2-003-green is the current known-good baseline.

---

# 26. Roadmap

Current:

    R2-003 GREEN
        |
        v
    Repository / Documentation Governance
        |
        v
    R2-004
        |
        v
    Greeks Dependency Audit
        |
        v
    Quant Validation
        |
        v
    UI Integration
        |
        v
    Alerts
        |
        v
    Production Hardening
        |
        v
    Live Readiness

---

# 27. Core Architectural Principles

1. Backend trading logic is authoritative.
2. Direction is independent from score polarity.
3. Quality and direction must remain separate concepts.
4. Strategies must preserve authoritative direction.
5. Execution must validate decisions before trade generation.
6. Replay and backtesting should use the same decision architecture.
7. UI must consume backend contracts.
8. Risk controls must not depend on UI availability.
9. Providers must remain replaceable.
10. Every major milestone must have a reproducible regression baseline.
