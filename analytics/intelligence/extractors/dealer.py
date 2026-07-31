from __future__ import annotations

from analytics.intelligence.extractors.base_extractor import BaseExtractor


class DealerExtractor(BaseExtractor):
    """
    Extracts dealer positioning and exposure information
    from RuntimeContext.
    """

    def extract(
        self,
        ctx,
        record,
    ):

        dealer = getattr(ctx, "dealer", None)

        if dealer is None:
            return

        record.dealer_gamma = getattr(
            dealer,
            "gamma_position",
            "",
        )

        record.dealer_delta = getattr(
            dealer,
            "delta_position",
            "",
        )

        record.gamma_exposure = getattr(
            dealer,
            "gamma_exposure",
            0.0,
        )

        record.delta_exposure = getattr(
            dealer,
            "delta_exposure",
            0.0,
        )

        record.gamma_wall = getattr(
            dealer,
            "gamma_wall",
            0.0,
        )

        record.gamma_flip = getattr(
            dealer,
            "gamma_flip",
            0.0,
        )

        record.zero_gamma = getattr(
            dealer,
            "zero_gamma",
            0.0,
        )