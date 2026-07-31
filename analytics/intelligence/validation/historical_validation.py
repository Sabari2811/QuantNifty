class HistoricalValidationEngine:

    def __init__(self):

        self.similarity = SimilarityEngine()

    def validate(
        self,
        current,
        memory,
    ):

        matches = self.similarity.search(

            current,

            memory.records,

            top_n=100,

        )

        #
        # Aggregate statistics
        #

        return HistoricalValidation(...)