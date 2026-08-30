from validation.live_session_freshness import evaluate_consecutive_freshness


def _item(ts):
    return {"provider_timestamp": ts, "freshness_status": "FRESH"}


def test_consecutive_timestamped_quotes_pass_freshness():
    cycles = [
        {"spot": _item("2026-08-30T09:15:00+00:00"), "option_chain": _item("2026-08-30T09:15:01+00:00")},
        {"spot": _item("2026-08-30T09:15:30+00:00"), "option_chain": _item("2026-08-30T09:15:31+00:00")},
    ]
    result = evaluate_consecutive_freshness(cycles)
    assert result["status"] == "PASS"
    assert result["timestamped_cycles"] == 2


def test_any_unverified_cycle_fails_closed():
    cycles = [
        {"spot": _item("2026-08-30T09:15:00+00:00"), "option_chain": _item("2026-08-30T09:15:01+00:00")},
        {"spot": {"provider_timestamp": None, "freshness_status": "UNVERIFIED"}, "option_chain": _item("2026-08-30T09:15:31+00:00")},
    ]
    result = evaluate_consecutive_freshness(cycles)
    assert result["status"] == "NOT_VERIFIED"
    assert result["unverified_items"] == 1


def test_stale_cycle_fails_closed():
    cycles = [
        {"spot": _item("2026-08-30T09:15:00+00:00"), "option_chain": _item("2026-08-30T09:15:01+00:00")},
        {"spot": {"provider_timestamp": "2026-08-30T08:00:00+00:00", "freshness_status": "STALE"}, "option_chain": _item("2026-08-30T09:15:31+00:00")},
    ]
    result = evaluate_consecutive_freshness(cycles)
    assert result["status"] == "FAIL"
    assert result["stale_items"] == 1
