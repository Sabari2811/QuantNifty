class ConsoleDashboard:

    WIDTH = 70

    def line(self):
        print("-" * self.WIDTH)

    def title(self, text):
        print()
        print("=" * self.WIDTH)
        print(text.center(self.WIDTH))
        print("=" * self.WIDTH)

    def section(self, title):
        print()
        self.line()
        print(title)
        self.line()

    def value(self, label, value):
        print(f"{label:<28}: {value}")

    def show(self, ctx):

        analytics = ctx.analytics

        dealer = analytics.get("dealer", {})
        dealer_flow = analytics.get("dealer_flow", {})
        probability = analytics.get("probability", {})
        signal = analytics.get("signal", {})
        technical = analytics.get("technical", {})
        trade = analytics.get("trade_plan", {})
        score = analytics.get("institutional_score", {})
        liquidity = analytics.get("liquidity", {})
        expected = analytics.get("expected_move", {})
        atr = analytics.get("atr", {})

        self.title("QUANTNIFTY LIVE SUMMARY")

        self.section("MARKET")

        self.value("Spot", ctx.spot)
        self.value("Expiry", ctx.expiry)

        self.section("DEALER")

        self.value("Dealer Gamma", dealer.get("dealer_gamma"))
        self.value("Market Mode", dealer.get("market_mode"))
        self.value("Dealer Delta", dealer_flow.get("dealer_delta"))
        self.value("Dealer Hedge", dealer_flow.get("dealer_hedging"))

        self.section("MARKET STRUCTURE")

        ms = analytics.get("market_structure", {})

        self.value("Structure", ms.get("structure"))
        self.value("Bias", ms.get("bias"))
        self.value("Confidence", ms.get("confidence"))

        self.section("LIQUIDITY")

        self.value("Support", liquidity.get("support"))
        self.value("Resistance", liquidity.get("resistance"))
        self.value("Call Wall", liquidity.get("call_wall"))
        self.value("Put Wall", liquidity.get("put_wall"))

        self.section("EXPECTED MOVE")

        self.value("Lower", expected.get("lower"))
        self.value("Upper", expected.get("upper"))

        self.section("TECHNICAL")

        ema = technical.get("ema", {})
        rsi = technical.get("rsi", {})
        vwap = technical.get("vwap", {})
        adx = technical.get("adx", {})

        self.value("EMA Trend", ema.get("trend"))
        self.value("RSI", rsi.get("rsi"))
        self.value("VWAP", vwap.get("position"))
        self.value("ADX", adx.get("adx"))

        self.section("VOLATILITY")

        self.value("ATR", atr.get("atr"))
        self.value("Volatility", atr.get("volatility"))

        self.section("INSTITUTIONAL SCORE")

        institutional = score.get("institutional", {})

        self.value("Score", institutional.get("score"))
        self.value("Grade", institutional.get("grade"))
        self.value("Signal", institutional.get("signal"))

        self.section("PREDICTION")

        self.value(
            "Bullish %",
            probability.get("bullish_probability")
        )

        self.value(
            "Bearish %",
            probability.get("bearish_probability")
        )

        self.value(
            "Confidence",
            probability.get("confidence")
        )

        self.section("TRADE")

        self.value("Signal", signal.get("signal"))
        self.value("Strike", trade.get("recommended_strike"))
        self.value("Option", trade.get("option_type"))
        self.value("Entry", trade.get("entry"))
        self.value("Stop", trade.get("stop_loss"))
        self.value("Target1", trade.get("target1"))
        self.value("Target2", trade.get("target2"))

        reasons = trade.get("reasons", [])

        if reasons:

            print()

            print("Reasons")

            for r in reasons:
                print(f"  • {r}")