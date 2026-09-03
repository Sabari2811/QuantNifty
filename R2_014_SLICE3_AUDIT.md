# R2-014 Slice 3 Audit — Runtime Analytics Handoff

## Audit status

**Baseline:** audit-complete / implementation-ready for a deterministic runtime-handoff contract slice.
**Branch:** `r2-011-canonical-snapshot-provenance`
**Audit basis:** current branch HEAD after R2-014 Slice 2.

## Boundary under audit

`AnalyticsPipeline.run()` → `LiveEngine.ctx.analytics` → `MarketSnapshot.analytics` → `SnapshotRecorder.analytics.json` → `ReplayLoader.analytics`.

## Evidence-led findings

1. `AnalyticsPipeline.run()` constructs a typed `MarketContext` and explicitly populates the canonical analytics fields, including `market_map`.
2. The same pipeline returns an analytics dictionary containing the canonical analytics keys plus structural entries such as `context` and `greeks`.
3. `LiveEngine._run_analytics()` assigns that complete pipeline result dictionary directly to `self.ctx.analytics` in normal live execution. Replay-recompute has an explicit expected-analytics branch and is intentionally not changed by this slice.
4. `MarketSnapshot.save()` copies the runtime analytics dictionary without filtering or recomputation.
5. `SnapshotRecorder.save()` persists `ctx.analytics` as `analytics.json`, and `ReplayLoader` restores that artifact as the replay analytics dictionary.
6. Therefore the current runtime path does carry the complete canonical analytics surface, but there is no regression contract proving the relationship between the typed `MarketContext` surface, the pipeline return dictionary, and the runtime assignment.
7. The existing Slice 2 test proves recorder/replay preservation from an artificial `ctx.analytics` payload; it does not prove production pipeline output contains the same canonical fields.

## Slice 3 scope decision

**Approved implementation slice:** add a deterministic structural regression contract that proves:

- every canonical analytics field declared in `MarketContext` is assigned by `AnalyticsPipeline.run()`;
- every canonical analytics field is present in the pipeline return dictionary;
- the runtime path assigns the pipeline result to `RuntimeContext.analytics` in normal execution;
- the test remains provider/network independent.

No production analytics calculation, snapshot format, replay format, decision/intelligence semantics, provider behavior, or UI behavior will change.

## Explicit non-goals

- No filtering or restructuring of the existing `ctx.analytics` envelope.
- No removal of the `context` or `greeks` return entries.
- No new snapshot artifact.
- No provider/live-network test dependency.
- No changes to replay-recompute semantics.
- No claim of full end-to-end runtime validation until the local regression suite is executed.

## Validation plan

1. Targeted Slice 1 + Slice 2 + Slice 3 structural tests.
2. Existing replay/backward-compatibility tests affected by analytics persistence.
3. Full pytest suite.
4. No new live-provider evidence required unless implementation unexpectedly changes runtime/provider behavior.

## Exit criteria

- [ ] Slice 3 regression committed.
- [ ] Targeted regression passes locally.
- [ ] Existing replay compatibility regression passes locally.
- [ ] Full regression passes locally.
- [ ] Master checklist updated only from actual evidence.
- [ ] Project state updated with actual implementation/test evidence.
