# QuantNifty Release Log

## R2-003 — Direction-Aware Regression Stabilization

### Git

Commit:

    696b535

Tag:

    R2-003-green

### Objective

Stabilize the direction-aware decision architecture and bring the complete regression suite to a green state.

### Completed

- Direction-aware scoring
- Direction quality separation
- Directional score adapter
- Directional snapshot adapter
- Strategy direction preservation
- Authoritative DecisionBuilder direction
- DecisionEngine runtime direction
- Trade validation improvements
- Backtest regression repair
- Decision pipeline regression repair
- Gamma Flip import correction
- OI Engine test isolation
- Session Manager test isolation

### Regression

    65 passed
    0 failed
    0 collection errors
    1 warning

### Warning

`py_vollib` deprecation warning remains.

### Next

R2-004 — Greeks dependency audit and deprecation cleanup.
