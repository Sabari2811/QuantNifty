# QuantNifty Backend / UI Mapping

## Purpose

This document defines which backend component owns each piece of information displayed by the UI.

## Market State

| UI | Backend authority |
|---|---|
| Spot | Market Snapshot / provider |
| Regime | Market Analyzer / Regime Engine |
| Bias | Market Analyzer |
| ATR | Analytics |
| Expected Move | Analytics |
| PCR | Analytics |
| Institutional state | Analytics |

## Dealer Intelligence

| UI | Backend authority |
|---|---|
| GEX | Exposure analytics |
| DEX | Exposure analytics |
| Gamma Flip | Gamma Flip detector |
| Gamma Wall | Gamma Wall detector |
| Call Wall | Dealer analytics |
| Put Wall | Dealer analytics |
| Dealer positioning | Dealer analytics |
| OI Flow | OI Flow Engine |
| IV Skew | IV analytics |

## Decision

| UI | Backend authority |
|---|---|
| Direction | Direction-aware decision pipeline |
| Quality | Scoring Engine |
| Confidence | Decision / scoring layer |
| Score breakdown | Scoring Engine |
| Strategy | Strategy Selector |
| Reasons | Decision / scoring pipeline |
| Validation | Trade Validator |

## Trade

| UI | Backend authority |
|---|---|
| Contract | Strike / execution selection |
| Entry | Execution Engine |
| Stop loss | Risk / execution layer |
| Target 1 | Target Selector |
| Target 2 | Target Selector |
| Lots | Execution Planner |
| Risk amount | Risk Engine |
| Risk/reward | Execution / validation |
| Trade quality | Trade Validator |

## Replay

| UI | Backend authority |
|---|---|
| Historical snapshot | Replay Session |
| Replay state | Replay Controller |
| Signal timeline | Decision pipeline |
| Trade timeline | Execution / Paper Broker |
| P&L | Backtest Engine |
| Drawdown | Performance analytics |

## Runtime

| UI | Backend authority |
|---|---|
| Provider status | Provider Manager |
| Data freshness | Runtime / provider layer |
| Analytics status | Analytics pipeline |
| Decision status | Decision Engine |
| Execution status | Execution Engine |
| System errors | Runtime diagnostics |

## Contract Principle

The UI displays backend state.

The UI does not independently determine trading decisions.
