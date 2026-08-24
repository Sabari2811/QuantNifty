import pandas as pd

from engine.greeks_engine import GreeksEngine


class LiveGreeksEngine:

    def __init__(self):
        self.greeks = GreeksEngine()

    def calculate_chain_greeks(
        self,
        option_chain: pd.DataFrame,
        spot_price: float,
        expiry,
        risk_free_rate=0.06
    ):
        """Calculate Greeks for the complete live option chain.

        The canonical GreeksEngine owns time-to-expiry calculation. A
        contract-level calculation failure is represented by missing Greek
        fields so one bad quote cannot discard the complete option chain.
        """
        if option_chain is None:
            return pd.DataFrame()

        if option_chain.empty:
            return option_chain.copy()

        df = option_chain.copy()

        ce_iv, ce_delta, ce_gamma, ce_theta, ce_vega, ce_rho = ([] for _ in range(6))
        pe_iv, pe_delta, pe_gamma, pe_theta, pe_vega, pe_rho = ([] for _ in range(6))

        for _, row in df.iterrows():
            strike = row["Strike"]

            try:
                ce = self.greeks.calculate_greeks(
                    option_price=row["CE_LTP"],
                    spot_price=spot_price,
                    strike_price=strike,
                    expiry=expiry,
                    option_type="CE",
                    risk_free_rate=risk_free_rate,
                )
            except ValueError:
                ce = {key: None for key in ("iv", "delta", "gamma", "theta", "vega", "rho")}

            ce_iv.append(ce["iv"])
            ce_delta.append(ce["delta"])
            ce_gamma.append(ce["gamma"])
            ce_theta.append(ce["theta"])
            ce_vega.append(ce["vega"])
            ce_rho.append(ce["rho"])

            try:
                pe = self.greeks.calculate_greeks(
                    option_price=row["PE_LTP"],
                    spot_price=spot_price,
                    strike_price=strike,
                    expiry=expiry,
                    option_type="PE",
                    risk_free_rate=risk_free_rate,
                )
            except ValueError:
                pe = {key: None for key in ("iv", "delta", "gamma", "theta", "vega", "rho")}

            pe_iv.append(pe["iv"])
            pe_delta.append(pe["delta"])
            pe_gamma.append(pe["gamma"])
            pe_theta.append(pe["theta"])
            pe_vega.append(pe["vega"])
            pe_rho.append(pe["rho"])

        df["CE_IV"] = ce_iv
        df["CE_DELTA"] = ce_delta
        df["CE_GAMMA"] = ce_gamma
        df["CE_THETA"] = ce_theta
        df["CE_VEGA"] = ce_vega
        df["CE_RHO"] = ce_rho

        df["PE_IV"] = pe_iv
        df["PE_DELTA"] = pe_delta
        df["PE_GAMMA"] = pe_gamma
        df["PE_THETA"] = pe_theta
        df["PE_VEGA"] = pe_vega
        df["PE_RHO"] = pe_rho

        return df
