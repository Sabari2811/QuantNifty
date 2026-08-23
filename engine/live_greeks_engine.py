from datetime import datetime

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
        """
        Calculate Greeks for the complete live option chain.

        Input:
            option_chain:
                DataFrame containing CE/PE LTP and Strike.

            spot_price:
                Current underlying/index spot.

            expiry:
                Option expiry datetime/date.

        Output:
            Copy of option_chain enriched with:

                CE_IV
                CE_DELTA
                CE_GAMMA
                CE_THETA
                CE_VEGA
                CE_RHO

                PE_IV
                PE_DELTA
                PE_GAMMA
                PE_THETA
                PE_VEGA
                PE_RHO
        """

        if option_chain is None:

            return pd.DataFrame()

        if option_chain.empty:

            return option_chain.copy()

        df = option_chain.copy()

        expiry_date = pd.to_datetime(expiry)

        today = datetime.today()

        days = (expiry_date - today).days

        if days <= 0:

            days = 1

        time_to_expiry = days / 365

        # =====================================================
        # CE Greeks
        # =====================================================

        ce_iv = []
        ce_delta = []
        ce_gamma = []
        ce_theta = []
        ce_vega = []
        ce_rho = []

        # =====================================================
        # PE Greeks
        # =====================================================

        pe_iv = []
        pe_delta = []
        pe_gamma = []
        pe_theta = []
        pe_vega = []
        pe_rho = []

        # =====================================================
        # Calculate Greeks Strike-by-Strike
        # =====================================================

        for _, row in df.iterrows():

            strike = row["Strike"]

            # -------------------------------------------------
            # CE
            # -------------------------------------------------

            ce = self.greeks.calculate_greeks(
                option_price=row["CE_LTP"],
                spot_price=spot_price,
                strike_price=strike,
                time_to_expiry=time_to_expiry,
                option_type="CE",
                risk_free_rate=risk_free_rate
            )

            ce_iv.append(ce["iv"])
            ce_delta.append(ce["delta"])
            ce_gamma.append(ce["gamma"])
            ce_theta.append(ce["theta"])
            ce_vega.append(ce["vega"])
            ce_rho.append(ce["rho"])

            # -------------------------------------------------
            # PE
            # -------------------------------------------------

            pe = self.greeks.calculate_greeks(
                option_price=row["PE_LTP"],
                spot_price=spot_price,
                strike_price=strike,
                time_to_expiry=time_to_expiry,
                option_type="PE",
                risk_free_rate=risk_free_rate
            )

            pe_iv.append(pe["iv"])
            pe_delta.append(pe["delta"])
            pe_gamma.append(pe["gamma"])
            pe_theta.append(pe["theta"])
            pe_vega.append(pe["vega"])

            # IMPORTANT:
            # PE Rho was previously missing.
            pe_rho.append(pe["rho"])

        # =====================================================
        # Attach CE Greeks
        # =====================================================

        df["CE_IV"] = ce_iv
        df["CE_DELTA"] = ce_delta
        df["CE_GAMMA"] = ce_gamma
        df["CE_THETA"] = ce_theta
        df["CE_VEGA"] = ce_vega
        df["CE_RHO"] = ce_rho

        # =====================================================
        # Attach PE Greeks
        # =====================================================

        df["PE_IV"] = pe_iv
        df["PE_DELTA"] = pe_delta
        df["PE_GAMMA"] = pe_gamma
        df["PE_THETA"] = pe_theta
        df["PE_VEGA"] = pe_vega
        df["PE_RHO"] = pe_rho

        return df