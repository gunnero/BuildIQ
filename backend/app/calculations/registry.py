from typing import Optional

from app.calculations.base import BaseCalculationEngine
from app.calculations.painting import PaintingCalculationEngine


class PlaceholderCalculationEngine(BaseCalculationEngine):
    def __init__(self, engine_type: str) -> None:
        self.engine_type = engine_type


class CalculationEngineRegistry:
    def __init__(self) -> None:
        self._engines: dict[str, BaseCalculationEngine] = {}

    def register(self, engine: BaseCalculationEngine) -> None:
        self._engines[engine.engine_type] = engine

    def get(self, engine_type: str) -> Optional[BaseCalculationEngine]:
        return self._engines.get(engine_type)

    def list(self) -> list[BaseCalculationEngine]:
        return [self._engines[key] for key in sorted(self._engines.keys())]


calculation_engine_registry = CalculationEngineRegistry()
calculation_engine_registry.register(PaintingCalculationEngine())

for registered_engine_type in (
    "tiles",
    "knauf",
    "flooring",
    "concrete",
    "facade",
):
    calculation_engine_registry.register(PlaceholderCalculationEngine(registered_engine_type))
