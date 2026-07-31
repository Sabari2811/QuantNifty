from decision.models import Decision
from decision.models.option_contract import OptionContract
from decision.execution.risk_engine import RiskEngine

decision = Decision()

decision.trade.contract = OptionContract(

    strike=24400,

    option_type="CE",

    ltp=182.45,

    iv=22

)

decision = RiskEngine().build(decision)

print()

print("=" * 70)

print(decision.trade.stop_loss)

print("=" * 70)