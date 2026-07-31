from decision.context import DecisionContext

ctx = DecisionContext()

ctx.signal = "BUY CALL"

ctx.confidence = 91

ctx.entry = 180

ctx.stop_loss = 130

ctx.target1 = 260

ctx.reasons.append("Dealer LONG")

print(ctx)