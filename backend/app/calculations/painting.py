from typing import Any, Optional, Union

from app.calculations.base import (
    BaseCalculationEngine,
    CalculationEngineResult,
    CalculationExecutionContext,
    CalculationLineItemResult,
)
from app.models.material import Material
from app.models.measurement import MeasurementItem
from app.services.materials import get_active_material_for_company
from app.services.measurements import (
    get_active_measurement_set_for_company,
    get_active_room_for_company,
    room_computed_values,
)
from app.services.procurement import resolve_material_price


def rounded(value: Optional[float]) -> Optional[float]:
    if value is None:
        return None
    return round(float(value), 4)


def failure_result(error_code: str, message: str, **extra: Any) -> CalculationEngineResult:
    output_payload: dict[str, Any] = {
        "error_code": error_code,
        "message": message,
    }
    output_payload.update(extra)
    return CalculationEngineResult(status="failed", output_payload=output_payload)


class PaintingCalculationEngine(BaseCalculationEngine):
    engine_type = "painting"
    engine_version = "painting-1"
    implemented = True
    status = "implemented"

    def execute(
        self,
        input_payload: dict[str, Any],
        context: Optional[CalculationExecutionContext] = None,
    ) -> CalculationEngineResult:
        if context is None:
            return failure_result(
                "calculation_context_missing",
                "Потребен е контекст за пресметка на бојадисување.",
            )
        if context.project_id is None:
            return failure_result(
                "project_required",
                "Проектот е задолжителен за пресметка на бојадисување.",
            )

        parsed = self.parse_input(input_payload)
        if isinstance(parsed, CalculationEngineResult):
            return parsed

        paint_material = self.load_material(
            context,
            material_id=parsed["paint_material_id"],
        )
        primer_material = self.load_material(
            context,
            material_id=parsed["primer_material_id"],
        )

        waste_percentage = parsed["waste_percentage"]
        if waste_percentage is None:
            waste_percentage = self.default_waste_percentage(paint_material, primer_material)

        areas = self.resolve_areas(context)
        if isinstance(areas, CalculationEngineResult):
            return areas

        selected_area = self.selected_area(
            wall_area_net=areas["wall_area_net_m2"],
            ceiling_area=areas["ceiling_area_m2"],
            include_walls=parsed["include_walls"],
            include_ceiling=parsed["include_ceiling"],
        )
        if selected_area <= 0:
            return failure_result(
                "painting_area_missing",
                "Не е пронајдена употреблива површина за избраниот опсег на бојадисување.",
            )

        paint_coverage = None
        primer_coverage = None
        if paint_material is not None:
            paint_coverage = self.material_coverage_m2_per_liter(paint_material)
            if paint_coverage is None:
                return failure_result(
                    "material_coverage_missing",
                    "Материјалот за боја мора да има покривност компатибилна со m2/liter.",
                    material_id=paint_material.id,
                )
        if primer_material is not None:
            primer_coverage = self.material_coverage_m2_per_liter(primer_material)
            if primer_coverage is None:
                return failure_result(
                    "material_coverage_missing",
                    "Прајмер материјалот мора да има покривност компатибилна со m2/liter.",
                    material_id=primer_material.id,
                )

        waste_factor = 1 + waste_percentage / 100
        paint_area_with_coats = selected_area * parsed["coats"]
        paint_area_with_waste = paint_area_with_coats * waste_factor
        paint_required_liters = (
            paint_area_with_waste / paint_coverage
            if paint_coverage is not None
            else None
        )
        primer_required_liters = self.primer_liters(
            selected_area=selected_area,
            primer_coats=parsed["primer_coats"],
            waste_factor=waste_factor,
            primer_coverage=primer_coverage,
        )

        warnings: list[str] = []
        paint_cost, paint_price_payload = self.material_cost_payload(
            context,
            material=paint_material,
            quantity=paint_required_liters,
            warning_label="материјалот за боја",
            warnings=warnings,
        )
        primer_cost, primer_price_payload = self.material_cost_payload(
            context,
            material=primer_material,
            quantity=primer_required_liters,
            warning_label="прајмер материјалот",
            warnings=warnings,
        )
        labor_cost = (
            selected_area * parsed["labor_rate_per_m2"]
            if parsed["labor_rate_per_m2"] is not None
            else None
        )
        total_cost = sum(
            cost
            for cost in (paint_cost, primer_cost, labor_cost)
            if cost is not None
        )

        line_items = self.line_items(
            paint_material=paint_material,
            paint_required_liters=paint_required_liters,
            paint_cost=paint_cost,
            paint_price_payload=paint_price_payload,
            primer_material=primer_material,
            primer_required_liters=primer_required_liters,
            primer_cost=primer_cost,
            primer_price_payload=primer_price_payload,
            labor_rate_per_m2=parsed["labor_rate_per_m2"],
            labor_cost=labor_cost,
            selected_area=selected_area,
        )

        output_payload = {
            "selected_area_m2": rounded(selected_area),
            "wall_area_net_m2": rounded(areas["wall_area_net_m2"]),
            "ceiling_area_m2": rounded(areas["ceiling_area_m2"]),
            "total_paintable_area_m2": rounded(areas["total_paintable_area_m2"]),
            "coats": parsed["coats"],
            "primer_coats": parsed["primer_coats"],
            "waste_percentage": rounded(waste_percentage),
            "paint_required_liters": rounded(paint_required_liters),
            "primer_required_liters": rounded(primer_required_liters),
            "paint_material_cost": rounded(paint_cost),
            "primer_material_cost": rounded(primer_cost),
            "labor_cost": rounded(labor_cost),
            "total_cost": rounded(total_cost),
            "assumptions": [
                areas["source"],
                "Покривноста на бојата и прајмерот се толкува како m2/liter.",
                "Процентот за отпад се применува на количините за боја и прајмер.",
            ],
            "warnings": warnings,
            "notes": parsed["notes"],
        }
        return CalculationEngineResult(
            status="completed",
            output_payload=output_payload,
            line_items=line_items,
        )

    def parse_input(
        self,
        input_payload: dict[str, Any],
    ) -> Union[dict[str, Any], CalculationEngineResult]:
        include_ceiling = self.boolean_input(input_payload, "include_ceiling", True)
        include_walls = self.boolean_input(input_payload, "include_walls", True)
        if include_ceiling is None or include_walls is None:
            return failure_result(
                "invalid_painting_input",
                "Полињата за вклучување ѕидови и таван мора да бидат boolean вредности.",
            )
        if not include_ceiling and not include_walls:
            return failure_result(
                "painting_area_missing",
                "Мора да биде избран барем ѕид или таван за бојадисување.",
            )

        coats = self.integer_input(input_payload, "coats", 2)
        primer_coats = self.integer_input(input_payload, "primer_coats", 0)
        if coats is None or coats < 1:
            return failure_result(
                "invalid_painting_input",
                "Бројот на слоеви боја мора да биде најмалку 1.",
            )
        if primer_coats is None or primer_coats < 0:
            return failure_result(
                "invalid_painting_input",
                "Бројот на прајмер слоеви мора да биде најмалку 0.",
            )

        waste_percentage = self.optional_float(input_payload, "waste_percentage")
        if waste_percentage is not None and waste_percentage < 0:
            return failure_result(
                "invalid_painting_input",
                "Процентот за отпад не може да биде негативен.",
            )
        labor_rate = self.optional_float(input_payload, "labor_rate_per_m2")
        if labor_rate is not None and labor_rate < 0:
            return failure_result(
                "invalid_painting_input",
                "Цената за работа не може да биде негативна.",
            )

        return {
            "include_ceiling": include_ceiling,
            "include_walls": include_walls,
            "coats": coats,
            "primer_coats": primer_coats,
            "paint_material_id": input_payload.get("paint_material_id"),
            "primer_material_id": input_payload.get("primer_material_id"),
            "waste_percentage": waste_percentage,
            "labor_rate_per_m2": labor_rate,
            "notes": input_payload.get("notes"),
        }

    def boolean_input(
        self,
        input_payload: dict[str, Any],
        key: str,
        default: bool,
    ) -> Optional[bool]:
        value = input_payload.get(key, default)
        return value if isinstance(value, bool) else None

    def integer_input(
        self,
        input_payload: dict[str, Any],
        key: str,
        default: int,
    ) -> Optional[int]:
        value = input_payload.get(key, default)
        if isinstance(value, bool) or not isinstance(value, int):
            return None
        return value

    def optional_float(
        self,
        input_payload: dict[str, Any],
        key: str,
    ) -> Optional[float]:
        value = input_payload.get(key)
        if value is None:
            return None
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return None
        return float(value)

    def load_material(
        self,
        context: CalculationExecutionContext,
        *,
        material_id: Optional[str],
    ) -> Optional[Material]:
        if material_id is None:
            return None
        return get_active_material_for_company(
            context.db,
            company_id=context.company_id,
            material_id=material_id,
        )

    def default_waste_percentage(
        self,
        paint_material: Optional[Material],
        primer_material: Optional[Material],
    ) -> float:
        if paint_material is not None and paint_material.waste_percentage_default is not None:
            return float(paint_material.waste_percentage_default)
        if primer_material is not None and primer_material.waste_percentage_default is not None:
            return float(primer_material.waste_percentage_default)
        return 10.0

    def resolve_areas(
        self,
        context: CalculationExecutionContext,
    ) -> Union[dict[str, Union[float, str]], CalculationEngineResult]:
        if context.room_id is not None:
            room = get_active_room_for_company(
                context.db,
                company_id=context.company_id,
                room_id=context.room_id,
            )
            computed = room_computed_values(context.db, room=room)
            return {
                "wall_area_net_m2": computed["wall_area_net"],
                "ceiling_area_m2": computed["ceiling_area"],
                "total_paintable_area_m2": computed["total_paintable_area"],
                "source": "Користени се пресметаните површини од просторијата.",
            }

        if context.measurement_set_id is not None:
            measurement_set = get_active_measurement_set_for_company(
                context.db,
                company_id=context.company_id,
                measurement_set_id=context.measurement_set_id,
            )
            items = (
                context.db.query(MeasurementItem)
                .filter(
                    MeasurementItem.company_id == context.company_id,
                    MeasurementItem.measurement_set_id == measurement_set.id,
                    MeasurementItem.archived_at.is_(None),
                    MeasurementItem.unit == "m2",
                )
                .all()
            )
            values: dict[str, float] = {}
            for item in items:
                if item.name in {"wall_area", "ceiling_area", "paintable_area"}:
                    values[item.name] = values.get(item.name, 0.0) + float(item.quantity)
            if not values:
                return failure_result(
                    "painting_area_missing",
                    "Сетот мерења не содржи употреблива површина за бојадисување.",
                )
            wall_area = values.get("wall_area")
            ceiling_area = values.get("ceiling_area")
            paintable_area = values.get("paintable_area")
            if wall_area is None and ceiling_area is None and paintable_area is not None:
                wall_area = paintable_area
                ceiling_area = 0.0
            elif wall_area is None and paintable_area is not None:
                wall_area = max(paintable_area - (ceiling_area or 0.0), 0.0)
            elif ceiling_area is None and paintable_area is not None:
                ceiling_area = max(paintable_area - (wall_area or 0.0), 0.0)
            wall_area = wall_area or 0.0
            ceiling_area = ceiling_area or 0.0
            total_paintable_area = paintable_area if paintable_area is not None else wall_area + ceiling_area
            return {
                "wall_area_net_m2": wall_area,
                "ceiling_area_m2": ceiling_area,
                "total_paintable_area_m2": total_paintable_area,
                "source": "Користени се површините од сетот мерења.",
            }

        return failure_result(
            "painting_area_missing",
            "Не е дадена просторија или сет мерења со употреблива површина за бојадисување.",
        )

    def selected_area(
        self,
        *,
        wall_area_net: float,
        ceiling_area: float,
        include_walls: bool,
        include_ceiling: bool,
    ) -> float:
        selected = 0.0
        if include_walls:
            selected += wall_area_net
        if include_ceiling:
            selected += ceiling_area
        return selected

    def material_coverage_m2_per_liter(self, material: Material) -> Optional[float]:
        if material.coverage_value is None or material.coverage_value <= 0:
            return None
        if material.coverage_unit is None:
            return None
        normalized = material.coverage_unit.lower().replace(" ", "")
        compatible_units = {
            "m2/liter",
            "m2/l",
            "m2/litre",
            "m2perliter",
            "m2perl",
            "m²/liter",
            "m²/l",
        }
        if normalized not in compatible_units:
            return None
        return float(material.coverage_value)

    def primer_liters(
        self,
        *,
        selected_area: float,
        primer_coats: int,
        waste_factor: float,
        primer_coverage: Optional[float],
    ) -> Optional[float]:
        if primer_coats == 0:
            return 0.0
        if primer_coverage is None:
            return None
        return selected_area * primer_coats * waste_factor / primer_coverage

    def material_cost_payload(
        self,
        context: CalculationExecutionContext,
        *,
        material: Optional[Material],
        quantity: Optional[float],
        warning_label: str,
        warnings: list[str],
    ) -> tuple[Optional[float], dict[str, Any]]:
        payload: dict[str, Any] = {
            "unit_price": None,
            "currency": None,
            "price_source_type": None,
            "price_source_id": None,
        }
        if material is None or quantity is None:
            return None, payload
        resolved_price = resolve_material_price(
            context.db,
            company_id=context.company_id,
            project_id=context.project_id,
            material_id=material.id,
        )
        payload.update(
            {
                "unit_price": resolved_price.resolved_price,
                "currency": resolved_price.currency,
                "price_source_type": resolved_price.source_type,
                "price_source_id": resolved_price.source_id,
            }
        )
        if resolved_price.resolved_price is None:
            warnings.append(f"Не е пронајдена цена за {warning_label}.")
            return None, payload
        return quantity * resolved_price.resolved_price, payload

    def line_items(
        self,
        *,
        paint_material: Optional[Material],
        paint_required_liters: Optional[float],
        paint_cost: Optional[float],
        paint_price_payload: dict[str, Any],
        primer_material: Optional[Material],
        primer_required_liters: Optional[float],
        primer_cost: Optional[float],
        primer_price_payload: dict[str, Any],
        labor_rate_per_m2: Optional[float],
        labor_cost: Optional[float],
        selected_area: float,
    ) -> list[CalculationLineItemResult]:
        line_items: list[CalculationLineItemResult] = []
        if paint_material is not None:
            line_items.append(
                CalculationLineItemResult(
                    name="Боја",
                    description=paint_material.name,
                    unit="liter",
                    quantity=rounded(paint_required_liters),
                    payload={
                        "item_type": "material",
                        "material_id": paint_material.id,
                        "total_cost": rounded(paint_cost),
                        **paint_price_payload,
                    },
                )
            )
        if primer_material is not None:
            line_items.append(
                CalculationLineItemResult(
                    name="Прајмер",
                    description=primer_material.name,
                    unit="liter",
                    quantity=rounded(primer_required_liters),
                    payload={
                        "item_type": "material",
                        "material_id": primer_material.id,
                        "total_cost": rounded(primer_cost),
                        **primer_price_payload,
                    },
                )
            )
        if labor_rate_per_m2 is not None:
            line_items.append(
                CalculationLineItemResult(
                    name="Работна рака",
                    description="Бојадисерска работа",
                    unit="m2",
                    quantity=rounded(selected_area),
                    payload={
                        "item_type": "labor",
                        "unit_price": rounded(labor_rate_per_m2),
                        "total_cost": rounded(labor_cost),
                    },
                )
            )
        return line_items
