from monitoring.production_readiness import build_production_readiness


def test_production_readiness_is_fail_closed_without_required_configuration():
    state = build_production_readiness({})
    assert state.live_provider_configured is False
    assert state.live_validation_enabled is False
    assert state.durable_persistence_configured is False
    assert state.ready_for_production_infrastructure is False


def test_production_readiness_requires_both_durable_stores_and_live_provider():
    env = {
        "APITOKEN": "configured",
        "LIVE_VALIDATION_MODE": "true",
        "BRAIN_DATABASE_URL": "postgresql+psycopg://db/quantnifty",
        "LIVE_EVIDENCE_DATABASE_URL": "postgresql+psycopg://db/quantnifty",
    }
    state = build_production_readiness(env)
    assert state.live_provider_configured is True
    assert state.live_validation_enabled is True
    assert state.brain_database_configured is True
    assert state.evidence_database_configured is True
    assert state.durable_persistence_configured is True
    assert state.ready_for_production_infrastructure is True


def test_production_readiness_never_treats_one_database_as_durable():
    env = {
        "APITOKEN": "configured",
        "LIVE_VALIDATION_MODE": "true",
        "BRAIN_DATABASE_URL": "postgresql+psycopg://db/quantnifty",
    }
    state = build_production_readiness(env)
    assert state.brain_database_configured is True
    assert state.evidence_database_configured is False
    assert state.durable_persistence_configured is False
    assert state.ready_for_production_infrastructure is False
