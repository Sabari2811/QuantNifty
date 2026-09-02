from tools.validate_live_streamlit_ui import main


def test_live_streamlit_validator_constructs_controls_before_setting(monkeypatch):
    class FakeControl:
        def __init__(self):
            self.value = None

        def set_value(self, value):
            self.value = value
            return self

    class FakeState(dict):
        pass

    class FakeApp:
        instances = []

        def __init__(self):
            self.selectbox = []
            self.slider = []
            self.exception = []
            self.session_state = FakeState()
            self.runs = 0
            FakeApp.instances.append(self)

        def run(self, timeout=120):
            self.runs += 1
            if self.runs == 1:
                self.selectbox = [FakeControl()]
                self.slider = [FakeControl()]
            else:
                dashboard = type(
                    "Dashboard",
                    (),
                    {
                        "symbol": "NIFTY",
                        "cycle_no": 1,
                        "runtime_status": "IDLE",
                        "intelligence": None,
                        "decision_intelligence_consistency": None,
                        "data_provenance": None,
                        "option_chain_integrity": None,
                        "option_chain": None,
                        "greeks": None,
                    },
                )()
                self.session_state["_quantnifty_dashboard_audit"] = dashboard
                self.session_state["_quantnifty_ui_contract"] = {
                    "decision": {},
                    "intelligence": None,
                    "decision_intelligence_consistency": None,
                    "provenance": None,
                    "option_chain_integrity": None,
                    "option_chain": None,
                    "greeks": None,
                }

    class FakeAt:
        @classmethod
        def from_file(cls, path):
            assert path == "dashboard/app.py"
            return FakeApp()

    monkeypatch.setattr("tools.validate_live_streamlit_ui.AppTest", FakeAt)
    monkeypatch.setattr(
        "tools.validate_live_streamlit_ui.adapt_decision",
        lambda dashboard: {},
    )
    monkeypatch.setattr(
        "tools.validate_live_streamlit_ui.compare_dashboard_ui_runtime",
        lambda dashboard: {"gaps": ["forced_test_gap"]},
    )
    monkeypatch.setattr(
        "tools.validate_live_streamlit_ui.build_live_reconciliation",
        lambda dashboard: {"gaps": []},
    )
    monkeypatch.setattr(
        "tools.validate_live_streamlit_ui.pd.testing.assert_frame_equal",
        lambda left, right: None,
    )
    monkeypatch.setattr(
        "tools.validate_live_streamlit_ui.json.dumps",
        lambda *args, **kwargs: "{}",
    )
    monkeypatch.setattr("sys.argv", ["validate_live_streamlit_ui.py"])

    result = main()
    fake_app = FakeApp.instances[-1]

    assert fake_app.runs == 2
    assert fake_app.selectbox[0].value == "NIFTY"
    assert fake_app.slider[0].value == 5
    assert result == 2
