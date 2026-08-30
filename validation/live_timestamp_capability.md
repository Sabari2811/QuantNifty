# Live Quote Timestamp Capability

## R2-013 gate

The INDMoney REST quote path currently preserves a provider timestamp when the response supplies one, and canonical provenance correctly remains `UNVERIFIED` when it does not.

This document records the capability boundary so the validator does not manufacture freshness from local acquisition time.

## Acceptance

- Provider timestamp present and parseable -> canonical `provider_timestamp` populated.
- Provider timestamp absent -> freshness remains `UNVERIFIED`.
- Provider timestamp in the future -> freshness verification rejected.
- Timestamp-bearing live source/session is required to close the live quote freshness gate.

## Current status

The current repository does not contain an implemented INDMoney streaming/WebSocket adapter. Therefore no code is being added that pretends streaming freshness is available.

Next implementation target is a real provider streaming adapter based on the provider's authenticated feed contract, followed by runtime/session tests using captured provider messages.
