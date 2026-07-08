from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.material import (
    Material,
    MaterialCategory,
    MaterialConsumptionRule,
    MaterialManufacturer,
    MaterialUnit,
)
from app.services.customers import not_found

MATERIAL_ENGINE_TYPES = {
    "painting",
    "tiles",
    "knauf",
    "flooring",
    "concrete",
    "facade",
}

DEFAULT_MATERIAL_UNITS = [
    ("piece", "Piece"),
    ("m", "Meter"),
    ("m2", "Square meter"),
    ("m3", "Cubic meter"),
    ("kg", "Kilogram"),
    ("liter", "Liter"),
    ("bag", "Bag"),
    ("bucket", "Bucket"),
    ("roll", "Roll"),
    ("hour", "Hour"),
]


def validation_error(message: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


def ensure_default_material_units(db: Session) -> bool:
    default_keys = [key for key, _ in DEFAULT_MATERIAL_UNITS]
    existing_units = (
        db.query(MaterialUnit)
        .filter(
            MaterialUnit.company_id.is_(None),
            MaterialUnit.key.in_(default_keys),
        )
        .all()
    )
    existing_keys = {unit.key for unit in existing_units}
    created = False
    for key, name in DEFAULT_MATERIAL_UNITS:
        if key in existing_keys:
            continue
        db.add(
            MaterialUnit(
                company_id=None,
                key=key,
                name=name,
                is_default=True,
            )
        )
        created = True
    if created:
        db.flush()
    return created


def validate_material_engine_type(value: str) -> str:
    if value not in MATERIAL_ENGINE_TYPES:
        raise validation_error("Невалиден тип на калкулатор.")
    return value


def get_active_material_category_for_company(
    db: Session,
    *,
    company_id: str,
    category_id: str,
) -> MaterialCategory:
    category = (
        db.query(MaterialCategory)
        .filter(
            MaterialCategory.id == category_id,
            MaterialCategory.company_id == company_id,
            MaterialCategory.archived_at.is_(None),
        )
        .one_or_none()
    )
    if category is None:
        raise not_found()
    return category


def get_active_material_manufacturer_for_company(
    db: Session,
    *,
    company_id: str,
    manufacturer_id: str,
) -> MaterialManufacturer:
    manufacturer = (
        db.query(MaterialManufacturer)
        .filter(
            MaterialManufacturer.id == manufacturer_id,
            MaterialManufacturer.company_id == company_id,
            MaterialManufacturer.archived_at.is_(None),
        )
        .one_or_none()
    )
    if manufacturer is None:
        raise not_found()
    return manufacturer


def get_active_material_unit_for_company(
    db: Session,
    *,
    company_id: str,
    unit_id: str,
) -> MaterialUnit:
    unit = (
        db.query(MaterialUnit)
        .filter(
            MaterialUnit.id == unit_id,
            MaterialUnit.archived_at.is_(None),
            or_(
                MaterialUnit.company_id == company_id,
                MaterialUnit.company_id.is_(None),
            ),
        )
        .one_or_none()
    )
    if unit is None:
        raise not_found()
    return unit


def get_active_material_for_company(
    db: Session,
    *,
    company_id: str,
    material_id: str,
) -> Material:
    material = (
        db.query(Material)
        .filter(
            Material.id == material_id,
            Material.company_id == company_id,
            Material.archived_at.is_(None),
        )
        .one_or_none()
    )
    if material is None:
        raise not_found()
    return material


def get_active_material_consumption_rule_for_company(
    db: Session,
    *,
    company_id: str,
    rule_id: str,
) -> MaterialConsumptionRule:
    rule = (
        db.query(MaterialConsumptionRule)
        .join(Material, MaterialConsumptionRule.material_id == Material.id)
        .filter(
            MaterialConsumptionRule.id == rule_id,
            MaterialConsumptionRule.company_id == company_id,
            MaterialConsumptionRule.archived_at.is_(None),
            Material.company_id == company_id,
            Material.archived_at.is_(None),
        )
        .one_or_none()
    )
    if rule is None:
        raise not_found()
    return rule


def validate_material_links(
    db: Session,
    *,
    company_id: str,
    category_id: Optional[str],
    manufacturer_id: Optional[str],
    unit_id: str,
) -> None:
    if category_id is not None:
        get_active_material_category_for_company(
            db,
            company_id=company_id,
            category_id=category_id,
        )
    if manufacturer_id is not None:
        get_active_material_manufacturer_for_company(
            db,
            company_id=company_id,
            manufacturer_id=manufacturer_id,
        )
    get_active_material_unit_for_company(
        db,
        company_id=company_id,
        unit_id=unit_id,
    )


def archive_material_category(category: MaterialCategory) -> MaterialCategory:
    category.archived_at = datetime.utcnow()
    return category


def archive_material_manufacturer(manufacturer: MaterialManufacturer) -> MaterialManufacturer:
    manufacturer.archived_at = datetime.utcnow()
    return manufacturer


def archive_material(material: Material) -> Material:
    material.is_active = False
    material.archived_at = datetime.utcnow()
    return material


def archive_material_consumption_rule(
    rule: MaterialConsumptionRule,
) -> MaterialConsumptionRule:
    rule.archived_at = datetime.utcnow()
    return rule
