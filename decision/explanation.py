from dataclasses import dataclass, field


@dataclass
class Explanation:
    """
    Human-readable explanation generated from
    the institutional decision engine.
    """

    # ======================================================
    # OVERVIEW
    # ======================================================

    title: str = ""

    summary: str = ""

    narrative: str = ""

    recommendation: str = ""

    confidence: int = 0

    # ======================================================
    # WHY
    # ======================================================

    why: list[str] = field(default_factory=list)

    # ======================================================
    # NEXT TRIGGERS
    # ======================================================

    triggers: list[str] = field(default_factory=list)

    # ======================================================
    # DETAILS
    # ======================================================

    strengths: list[str] = field(default_factory=list)

    weaknesses: list[str] = field(default_factory=list)

    warnings: list[str] = field(default_factory=list)

    observations: list[str] = field(default_factory=list)