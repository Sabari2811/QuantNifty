# QuantNifty UI Architecture

## Principle

The UI is a first-class QuantNifty component and evolves alongside the backend.

The UI must consume authoritative backend contracts. It must not independently recreate trading logic.

## Architecture

Backend:

    Data
      |
      v
    Analytics
      |
      v
    Decision Intelligence
      |
      v
    Execution / Validation
      |
      v
    API / WebSocket contracts
      |
      v
    UI

## UI Areas

### 1. Dashboard Foundation

- Live market state
- NIFTY / BANKNIFTY selection
- Market timestamp
- Provider status
- Data freshness
- Market regime

### 2. Market Intelligence

- Spot price
- VWAP
- CPR
- Camarilla
- Support / resistance
- Market structure
- Liquidity zones
- Expected move
- ATR
- India VIX

### 3. Dealer / Options Intelligence

- GEX
- DEX
- Gamma Flip
- Gamma Wall
- Call Wall
- Put Wall
- Dealer positioning
- OI concentration
- OI Flow
- PCR
- IV Skew

### 4. Decision Intelligence

The signal panel should display:

- Direction
- Quality score
- Confidence
- Market regime
- Score breakdown
- Reasons
- Validation state

Example:

    BUY CALL
    Quality: 82 / 100
    Confidence: 86%
    Regime: TRENDING

### 5. Trade Execution Panel

Display the backend-generated:

- Option contract
- Strike
- Entry
- Stop loss
- Target 1
- Target 2
- Risk / reward
- Risk amount
- Lots
- Trade quality
- Validation

The UI must not independently calculate these values.

### 6. Replay / Backtest Workbench

- Historical date selection
- Replay speed
- Play / pause / step
- Market snapshot
- Analytics state
- Signal timeline
- Trade timeline
- P&L
- Drawdown
- Trade journal

### 7. Runtime Monitor

- Provider status
- API latency
- Data freshness
- Analytics status
- Decision Engine status
- Execution status
- Error state
- Alert status

### 8. Research UI

- Strategy comparison
- Win rate
- Profit factor
- Expectancy
- Maximum drawdown
- Sharpe
- Average R
- CALL vs PUT
- Regime performance
- Time-of-day performance

### 9. Production Controls

Before live autonomous execution:

- Paper / Live mode indicator
- Kill switch
- Maximum daily loss
- Maximum trades
- Maximum lots
- Broker status
- API status
- Emergency stop
- Audit log

## UI Design Rule

Never duplicate:

- scoring logic
- direction logic
- risk calculations
- strike selection
- validation rules
- execution rules

The backend remains authoritative.
