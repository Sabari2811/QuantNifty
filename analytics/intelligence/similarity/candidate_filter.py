from __future__ import annotations


class CandidateFilter:
    """
    Narrows the search space before similarity scoring.
    """

    def filter(
        self,
        current,
        records,
    ):

        candidates = []

        for record in records:

            #
            # Same option side
            #
            if record.option_type != current.option_type:
                continue

            #
            # Same signal
            #
            if record.signal != current.signal:
                continue

            candidates.append(record)

        return candidates