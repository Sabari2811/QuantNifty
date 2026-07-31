from dataclasses import dataclass, field


@dataclass
class ValidationResult:

    valid: bool

    grade: str

    confidence: int

    risk_multiplier: float

    warnings: list = field(default_factory=list)