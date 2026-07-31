from decision.models import Decision
from decision.models.option_contract import OptionContract
from decision.execution.trade_quality_engine import TradeQualityEngine

decision = Decision()

decision.trade.risk_reward = 1.40

decision.trade.contract = OptionContract(

    strike=24400,

    option_type="CE",

    ltp=182.45,

    iv=12.6,

    oi=125000,

    volume=98000,

    delta=0.42

)

quality = TradeQualityEngine().score(

    decision

)

print()

print("=" * 70)

print("Trade Quality :", quality)

print("=" * 70)