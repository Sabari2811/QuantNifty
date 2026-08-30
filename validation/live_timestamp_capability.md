# Live Quote Timestamp Capability

## R2-013 gate

The INDstocks authenticated WebSocket price-feed adapter is implemented and preserves provider timestamps through the live quote coordinator into canonical runtime provenance. The REST quote path also preserves a provider timestamp when supplied and remains `UNVERIFIED` when it is absent.

The WebSocket path is explicitly opt-in and requires the real `INDMoneyProvider` plus `INDSTOCKS_WS_NIFTY_TOKEN`; test doubles cannot activate live networking through environment leakage.

## Acceptance

- Provider timestamp present and parseable -> canonical `provider_timestamp` populated.
- Provider timestamp absent on REST -> freshness remains `UNVERIFIED`.
- Provider timestamp in the future -> freshness verification rejected.
- Timestamp-bearing WebSocket tick -> canonical quote timestamp and age are derived from the provider timestamp, not local render/acquisition time.
- Live session validation must use an authenticated provider session and captured provider messages; synthetic timestamps do not close the live freshness gate.

## Current status

**Implementation complete; live-session evidence pending.**

Implemented components:

- `providers/indmoney_websocket.py` — authenticated timestamp-bearing transport adapter.
- `providers/live_quote_coordinator.py` — canonical live tick collection/normalization boundary.
- `engine/market_data_pipeline.py` — explicit live-feed wiring into canonical spot/option provenance.
- `tools/validate_live_session.py` — consecutive-cycle evidence runner.

The remaining acceptance step is a real market-session validation using the configured INDstocks WebSocket feed. No freshness gate is marked complete from mocks or locally generated timestamps.
