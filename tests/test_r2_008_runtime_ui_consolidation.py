def test_legacy_live_service_uses_same_canonical_runtime(monkeypatch):
    import app.services.live_service as live_service_module
    import dashboard.dashboard_controller as controller_module

    class FakeRuntime:
        pass

    runtime = FakeRuntime()

    monkeypatch.setattr(
        live_service_module,
        "RuntimeManager",
        lambda: runtime,
    )
    monkeypatch.setattr(
        controller_module,
        "RuntimeManager",
        lambda: runtime,
    )

    legacy_service = live_service_module.LiveService()
    canonical_controller = controller_module.DashboardController()

    assert legacy_service.runtime is canonical_controller.runtime


def test_runtime_manager_is_singleton_for_ui_adapters():
    from runtime.runtime_manager import RuntimeManager

    first = RuntimeManager()
    second = RuntimeManager()

    assert first is second
