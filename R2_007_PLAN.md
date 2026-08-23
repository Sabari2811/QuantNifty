# R2-007 Canonical Runtime → Dashboard Stabilization

## Scope
- Make DashboardController consume the canonical RuntimeManager/LiveEngine context.
- Eliminate the dashboard's duplicate market acquisition path from the active UI.
- Preserve existing DashboardData field contracts.
- Make the selected dashboard symbol the runtime symbol before each cycle.
- Do not add trading logic, change execution policy, or remove legacy modules in this milestone.

## Acceptance criteria
- DashboardController obtains spot, expiry, option chain, Greeks, analytics, intelligence, and runtime state from one RuntimeContext.
- RuntimeManager.run_once(symbol=...) sets the active symbol before LiveEngine.run_cycle().
- Existing tests remain green; add regression coverage for symbol propagation and single-runtime-source behavior.
