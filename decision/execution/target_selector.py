class TargetSelector:
    """
    Chooses the best profit target.

    Rules:

    BUY CALL
        nearest resistance above spot

    BUY PUT
        nearest support below spot
    """

    def select(self, decision, snapshot):

        spot = snapshot.spot

        dealer = snapshot.dealer

        move = snapshot.expected_move.get(

            "expected_move",

            100

        )

        levels = []

        # -----------------------------------
        # BUY CALL
        # -----------------------------------

        if decision.signal.name == "BUY CALL":

            for level in [

                dealer.get("gamma_wall"),

                dealer.get("call_wall"),

                spot + move

            ]:

                if level is not None and level > spot:

                    levels.append(level)

            if levels:

                levels.sort()

                return levels[0]

        # -----------------------------------
        # BUY PUT
        # -----------------------------------

        if decision.signal.name == "BUY PUT":

            for level in [

                dealer.get("put_wall"),

                dealer.get("gamma_flip"),

                spot - move

            ]:

                if level is not None and level < spot:

                    levels.append(level)

            if levels:

                levels.sort(reverse=True)

                return levels[0]

        return spot