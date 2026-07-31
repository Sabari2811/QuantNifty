from __future__ import annotations

from analytics.intelligence.similarity.candidate_filter import CandidateFilter
from analytics.intelligence.similarity.scorer import SimilarityScorer


class SimilarityEngine:

    def __init__(self):

        self.filter = CandidateFilter()

        self.scorer = SimilarityScorer()

    def search(
        self,
        current,
        history,
        top_n=20,
    ):

        candidates = self.filter.filter(

            current,

            history,

        )

        scored = []

        for record in candidates:

            similarity = self.scorer.score(

                current,

                record,

            )

            scored.append(

                (

                    similarity,

                    record,

                )

            )

        scored.sort(

            reverse=True,

            key=lambda x:x[0]

        )

        return scored[:top_n]