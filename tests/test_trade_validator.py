from decision.execution.trade_validator import TradeValidator
from decision.models import Decision
from decision.models.option_contract import OptionContract

decision = Decision()

decision.trade.entry = 182.45
decision.trade.risk_reward = 1.40

decision.trade.contract = OptionContract(
    strike=24400,
    option_type="CE",
    ltp=182.45,
    oi=125000,
    volume=98000
)

valid, reasons = TradeValidator().validate(decision)

print()
print("=" * 70)
print("Valid :", valid)
print("Reasons :", reasons)
print("=" * 70)