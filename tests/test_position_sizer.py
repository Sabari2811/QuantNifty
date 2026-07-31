from decision.models import Decision
from decision.execution.position_sizer import PositionSizer

decision = Decision()

decision.trade.entry = 182.45

decision.trade.stop_loss = 136.84

result = PositionSizer().size(

    decision,

    capital=500000,

    risk_percent=1,

    lot_size=75

)

print()

print("=" * 70)

print(result)

print("=" * 70)