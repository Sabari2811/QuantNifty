from monitoring.durable_store import _normalize_database_url


def test_render_postgresql_url_uses_psycopg3():
    assert (
        _normalize_database_url("postgresql://user:pass@host/db")
        == "postgresql+psycopg://user:pass@host/db"
    )


def test_legacy_postgres_url_uses_psycopg3():
    assert (
        _normalize_database_url("postgres://user:pass@host/db")
        == "postgresql+psycopg://user:pass@host/db"
    )


def test_existing_psycopg2_url_is_upgraded():
    assert (
        _normalize_database_url("postgresql+psycopg2://user:pass@host/db")
        == "postgresql+psycopg://user:pass@host/db"
    )


def test_sqlite_url_is_unchanged():
    assert _normalize_database_url("sqlite:///runtime.db") == "sqlite:///runtime.db"
