# QuantNifty Project Context

## Project

QuantNifty is a modular NIFTY options analytics, decision, execution, replay and backtesting platform.

## Current Provider

INDMoney / INDstocks is the active provider architecture.

Legacy Breeze code exists only in legacy areas and should not be reintroduced into the active provider architecture.

## Current Architecture

    Provider
       |
       v
    Instrument / Market Data
       |
       v
    Analytics
       |
       v
    Market Analysis
       |
       v
    Direction-aware Scoring
       |
       v
    Strategy Selection
       |
       v
    Decision Builder
       |
       v
    Execution Planning
       |
       v
    Trade Validation
       |
       v
    Paper / Replay / Backtest

## Current Git Baseline

Commit:

    696b535

Tag:

    R2-003-green

Regression:

    65 passed
    0 failures
    0 collection errors
    1 warning

## Current Engineering State

The direction-aware decision architecture is complete and regression-tested.

The next engineering task is R2-004:

    py_vollib dependency audit
    API compatibility check
    numerical comparison
    safe migration if appropriate
    full regression

## Product Roadmap

Backend and UI are both first-class project tracks.

Backend tracks:

- data providers
- analytics
- decision intelligence
- execution
- replay
- backtesting
- risk
- production hardening

UI tracks:

- live dashboard
- market intelligence
- dealer intelligence
- decision intelligence
- trade execution
- replay workbench
- runtime monitoring
- research
- portfolio intelligence
- production controls

## Important Design Principle

Backend trading logic is authoritative.

The UI must consume backend contracts and must not independently reproduce scoring, direction, risk, validation or execution logic.
