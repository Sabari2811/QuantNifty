from decision.models import Decision
from decision.option_contract import OptionContract
from decision.execution.premium.premium_engine import PremiumEngine

decision = Decision()

decision.trade.contract = OptionContract(

    strike=24400,

    option_type="CE",

    ltp=182.45

)

decision = PremiumEngine().build(decision)

print()

print("=" * 70)

print(decision.trade)

print("=" * 70)