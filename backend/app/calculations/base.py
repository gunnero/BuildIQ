from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True)
class CalculationLineItemResult:
    name: str
    description: Optional[str] = None
    unit: Optional[str] = None
    quantity: Optional[float] = None
    payload: Optional[dict[str, Any]] = None


@dataclass(frozen=True)
class CalculationEngineResult:
    status: str
    output_payload: dict[str, Any]
    line_items: list[CalculationLineItemResult] = field(default_factory=list)


class BaseCalculationEngine:
    engine_type = ""
    engine_version = "placeholder-1"
    implemented = False
    status = "placeholder"

    def validate_input(self, input_payload: dict[str, Any]) -> dict[str, Any]:
        return input_payload

    def execute(self, input_payload: dict[str, Any]) -> CalculationEngineResult:
        validated_input = self.validate_input(input_payload)
        return CalculationEngineResult(
            status="failed",
            output_payload={
                "error_code": "engine_not_implemented",
                "message": (
                    f"Calculation engine '{self.engine_type}' is registered "
                    "but not implemented yet."
                ),
                "engine_type": self.engine_type,
                "engine_version": self.engine_version,
                "implemented": self.implemented,
                "input_keys": sorted(validated_input.keys()),
            },
        )

    def metadata(self) -> dict[str, Any]:
        return {
            "engine_type": self.engine_type,
            "engine_version": self.engine_version,
            "implemented": self.implemented,
            "status": self.status,
        }
