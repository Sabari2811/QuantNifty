from analytics.oi.oi_flow_engine import OIFlowEngine
from providers.live_service import LiveService

ctx = LiveService().get_context()

oi = OIFlowEngine().analyze(ctx.greeks)

print("\n===== SUMMARY =====")
print(oi["summary"])

print("\n===== TABLE =====")
print(
    oi["table"][[
        "STRIKE",
        "CE_FLOW",
        "PE_FLOW"
    ]].head(10)
)