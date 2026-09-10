from types import SimpleNamespace

import pandas as pd

from dashboard.ui_data_contract import build_ui_data_contract, validate_ui_data_contract
from models.dashboard_data import DashboardData
from models.dealer_data import DealerData


def _dashboard():
    chain = pd.DataFrame([{"Strike": 25000, "CE_LTP": 150.0, "PE_LTP": 140.0}])
    greeks = chain.copy()
    dealer = DealerData(
        dealer_gamma="POSITIVE",
        market_mode="RANGE",
        support=24800,
        resistance=25200,
        gamma_flip=24950,
        gamma_wall=25000,
        expected_volatility="NORMAL",
        mean_reversion_probability=0.6,
        breakout_probability=0.4,
        total_gex=1234.5,
    )
    return DashboardData(
        provider="indmoney",
        symbol="NIFTY",
        spot=25020.0,
        expiry="09/08/2026 14:00",
        dealer=dealer,
        dealer_flow={"dealer_delta": 10},
        expected_move={"atm_strike": 25000, "expected_move": 290.0, "lower": 24730.0, "upper": 25310.0, "method": "ATM_STRADDLE"},
        max_pain={"max_pain": 25000, "call_oi": 1000, "put_oi": 1200, "total_oi": 2200},
        pcr={"oi_pcr": 1.2, "volume_pcr": 2.0, "sentiment": "BULLISH"},
        market_structure={"structure": "HH_HL", "bias": "BULLISH", "confidence": 80, "reason": "trend"},
        liquidity={"support": 24800, "resistance": 25200},
        probability={"bullish_probability": 60.0, "bearish_probability": 40.0, "confidence": 60.0, "reasons": ("r",)},
        signal={"signal": "BUY CALL", "confidence": 60.0},
        trade_plan={"signal": "BUY CALL", "recommended_strike": 25000, "option_type": "CE", "risk_reward": 2.0},
        risk={"capital_per_trade": 10000},
        institutional_score={"score": 75},
        analytics={"canonical": True},
        option_chain=chain,
        greeks=greeks,
        data_provenance=SimpleNamespace(source="indmoney"),
        option_chain_integrity={"status": "PASS"},
        intelligence={"direction": "BULLISH", "recommendation": "BUY CALL"},
        execution_intent=SimpleNamespace(symbol="NIFTY"),
        execution_result=SimpleNamespace(status="EXECUTED"),
        execution_lifecycle="EXECUTED",
        position=True,
        last_trade=SimpleNamespace(order_id="T1"),
        portfolio=SimpleNamespace(),
        position_recovery=SimpleNamespace(safe_to_continue=True),
        position_reconciliation=SimpleNamespace(status="MATCH"),
        journal=SimpleNamespace(),
        statistics={"total_pnl": 1500},
        risk_state=SimpleNamespace(),
        trade_status="EXECUTED",
        trade_block_reason="",
        runtime_status="IDLE",
        cycle_no=7,
    )


def test_contract_maps_exact_backend_values():
    dashboard = _dashboard()
    contract = build_ui_data_contract(dashboard)

    assert contract["identity"]["spot"] is dashboard.spot
    assert contract["identity"]["provider"] is dashboard.provider
    assert contract["market_banner"]["signal"] == dashboard.signal["signal"]
    assert contract["market_banner"]["recommended_strike"] == dashboard.trade_plan["recommended_strike"]
    assert contract["market_regime"]["total_gex"] == dashboard.dealer.total_gex
    assert contract["expected_move"] is dashboard.expected_move
    assert contract["max_pain"] is dashboard.max_pain
    assert contract["pcr"] is dashboard.pcr
    assert contract["market_structure"] is dashboard.market_structure
    assert contract["liquidity"] is dashboard.liquidity
    assert contract["trade_plan"] is dashboard.trade_plan
    assert contract["risk"] is dashboard.risk
    assert contract["institutional_score"] is dashboard.institutional_score
    assert contract["option_chain"] is dashboard.option_chain
    assert contract["greeks"] is dashboard.greeks
    assert contract["execution"]["intent"] is dashboard.execution_intent
    assert contract["execution"]["result"] is dashboard.execution_result
    assert contract["position_state"]["recovery"] is dashboard.position_recovery
    assert contract["position_state"]["reconciliation"] is dashboard.position_reconciliation
    assert validate_ui_data_contract(contract) == []


def test_contract_detects_decision_trade_plan_divergence():
    dashboard = _dashboard()
    dashboard.trade_plan["signal"] = "BUY PUT"
    contract = build_ui_data_contract(dashboard)
    errors = validate_ui_data_contract(contract)
    assert "decision.signal != trade_plan.signal" in errors
