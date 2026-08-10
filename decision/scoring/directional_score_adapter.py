class DirectionalScoreAdapter:
    """
    Converts direction + institutional quality into a signed decision score.

    Direction is authoritative.
    Institutional score represents quality/conviction.
    """

    VALID_DIRECTIONS = {"BUY CALL", "BUY PUT", "WAIT"}

    def adapt(self, direction, quality_score):
        if direction not in self.VALID_DIRECTIONS:
            raise ValueError(f"Unsupported direction: {direction}")

        quality = max(0, float(quality_score or 0))

        if direction == "BUY CALL":
            signed_score = quality
        elif direction == "BUY PUT":
            signed_score = -quality
        else:
            signed_score = 0

        return {
            "direction": direction,
            "quality_score": quality,
            "signed_score": signed_score,
        }