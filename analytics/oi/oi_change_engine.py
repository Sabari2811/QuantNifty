class OIChangeEngine:
    """
    Calculates OI changes between two snapshots.
    """

    def calculate(

        self,

        previous,

        current

    ):

        if previous is None:

            return {}

        previous = previous.get()
        current = current.get()

        result = {}

        for strike in current:

            if strike not in previous:
                continue

            old = previous[strike]
            new = current[strike]

            result[strike] = {

                "call_oi_change":

                    new["ce_oi"] - old["ce_oi"],

                "put_oi_change":

                    new["pe_oi"] - old["pe_oi"],

                "call_volume_change":

                    new["ce_volume"] - old["ce_volume"],

                "put_volume_change":

                    new["pe_volume"] - old["pe_volume"]

            }

        return result