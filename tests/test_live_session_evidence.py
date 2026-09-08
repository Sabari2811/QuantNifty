from pathlib import Path

from monitoring.live_session_evidence import JsonlLiveEvidenceStore, build_live_cycle_evidence


class Provenance:
    freshness_status = "FRESH"
    option_chain = type("Option", (), {"coverage_status": "COMPLETE", "integrity_status": "VALID"})()


class Ctx:
    cycle_no = 7
    spot = 25123.4
    runtime_status = "READY"
    trade_status = "BLOCKED"
    trade_block_reason = "PAPER_ONLY"
    data_provenance = Provenance()


def test_live_evidence_requires_explicit_live_provider():
    evidence = build_live_cycle_evidence(Ctx(), provider="INDMONEY", provider_mode="LIVE_PROVIDER")
    assert evidence.evidence_state == "VALID_LIVE"
    assert evidence.provider_mode == "LIVE_PROVIDER"


def test_missing_identity_cannot_be_certified_as_live():
    evidence = build_live_cycle_evidence(Ctx())
    assert evidence.evidence_state == "INVALID_NOT_LIVE"
    assert evidence.provider == "UNKNOWN"
    assert evidence.provider_mode == "UNKNOWN"


def test_non_live_mode_cannot_be_certified_as_live():
    evidence = build_live_cycle_evidence(Ctx(), provider="INDMONEY", provider_mode="REPLAY")
    assert evidence.evidence_state == "INVALID_NOT_LIVE"


def test_store_is_append_only_and_durable(tmp_path: Path):
    store = JsonlLiveEvidenceStore(tmp_path / "evidence.jsonl")
    evidence = build_live_cycle_evidence(Ctx(), provider="INDMONEY", provider_mode="LIVE_PROVIDER")
    store.append(evidence)
    store.append(evidence)
    assert store.count() == 2
