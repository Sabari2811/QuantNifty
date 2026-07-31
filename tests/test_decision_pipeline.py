snapshot = MarketSnapshot().save(...)

decision = DecisionEngine().build(snapshot)

print(decision)