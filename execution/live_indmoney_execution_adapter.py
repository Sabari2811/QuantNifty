from __future__ import annotations

from execution.execution_contract import ExecutionAction, ExecutionResult, ExecutionStatus, OrderIntent
from execution.indmoney_execution_result_mapper import map_indmoney_execution_result
from execution.indmoney_order_mapper import INDMoneyOrderRequest, build_indmoney_order_request
from execution.instrument_execution_resolver import ExecutionInstrument, InstrumentExecutionResolver


class LiveINDMoneyExecutionAdapter:
    """Provider-specific live execution adapter behind the canonical execution boundary."""

    def __init__(self, provider, instrument_resolver: InstrumentExecutionResolver):
        if provider is None:
            raise ValueError("Provider is required")
        if instrument_resolver is None:
            raise ValueError("Instrument resolver is required")
        self.provider = provider
        self.instrument_resolver = instrument_resolver

    def build_request(self, intent: OrderIntent) -> INDMoneyOrderRequest:
        instrument: ExecutionInstrument = self.instrument_resolver.resolve(intent)
        return build_indmoney_order_request(intent, instrument)

    def execute(self, intent: OrderIntent, decision=None) -> ExecutionResult:
        if intent is None:
            raise ValueError("Order intent is required")

        try:
            request = self.build_request(intent)
            response = self.provider.place_order(request)
        except Exception as exc:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                intent=intent,
                reason=f"INDMoney order submission failed: {exc}",
                raw=None,
            )

        try:
            return map_indmoney_execution_result(intent, response)
        except Exception as exc:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                intent=intent,
                reason=f"INDMoney execution response mapping failed: {exc}",
                raw=response,
            )
