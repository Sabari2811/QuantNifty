from dataclasses import dataclass


@dataclass
class AnalyticsResult:

    dealer: dict

    dealer_flow: dict

    expected_move: dict

    pcr: dict

    technical: dict

    probability: dict

    signal: dict

    decision: dict

    trade_plan: dict

    smart_strike: dict

    institutional_score: dict