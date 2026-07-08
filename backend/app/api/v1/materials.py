from fastapi import APIRouter, Depends, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.deps import get_current_company
from app.db.session import get_db
from app.models.identity import Company
from app.models.material import (
    Material,
    MaterialCategory,
    MaterialConsumptionRule,
    MaterialManufacturer,
    MaterialUnit,
)
from app.schemas.material import (
    MaterialCategoryCreate,
    MaterialCategoryResponse,
    MaterialCategoryUpdate,
    MaterialConsumptionRuleCreate,
    MaterialConsumptionRuleResponse,
    MaterialConsumptionRuleUpdate,
    MaterialCreate,
    MaterialManufacturerCreate,
    MaterialManufacturerResponse,
    MaterialManufacturerUpdate,
    MaterialResponse,
    MaterialUnitCreate,
    MaterialUnitResponse,
    MaterialUpdate,
)
from app.services.materials import (
    archive_material,
    archive_material_category,
    archive_material_consumption_rule,
    archive_material_manufacturer,
    ensure_default_material_units,
    get_active_material_category_for_company,
    get_active_material_consumption_rule_for_company,
    get_active_material_for_company,
    get_active_material_manufacturer_for_company,
    get_active_material_unit_for_company,
    validate_material_engine_type,
    validate_material_links,
    validation_error,
)

router = APIRouter(tags=["materials"])


def material_category_response(category: MaterialCategory) -> MaterialCategoryResponse:
    return MaterialCategoryResponse(
        id=category.id,
        company_id=category.company_id,
        name=category.name,
        description=category.description,
        archived_at=category.archived_at,
        created_at=category.created_at,
        updated_at=category.updated_at,
    )


def material_manufacturer_response(
    manufacturer: MaterialManufacturer,
) -> MaterialManufacturerResponse:
    return MaterialManufacturerResponse(
        id=manufacturer.id,
        company_id=manufacturer.company_id,
        name=manufacturer.name,
        website=manufacturer.website,
        note=manufacturer.note,
        archived_at=manufacturer.archived_at,
        created_at=manufacturer.created_at,
        updated_at=manufacturer.updated_at,
    )


def material_unit_response(unit: MaterialUnit) -> MaterialUnitResponse:
    return MaterialUnitResponse(
        id=unit.id,
        company_id=unit.company_id,
        key=unit.key,
        name=unit.name,
        description=unit.description,
        is_default=unit.is_default,
        archived_at=unit.archived_at,
        created_at=unit.created_at,
        updated_at=unit.updated_at,
    )


def material_response(material: Material) -> MaterialResponse:
    return MaterialResponse(
        id=material.id,
        company_id=material.company_id,
        name=material.name,
        sku=material.sku,
        description=material.description,
        category_id=material.category_id,
        manufacturer_id=material.manufacturer_id,
        unit_id=material.unit_id,
        coverage_value=material.coverage_value,
        coverage_unit=material.coverage_unit,
        package_quantity=material.package_quantity,
        waste_percentage_default=material.waste_percentage_default,
        is_active=material.is_active,
        archived_at=material.archived_at,
        created_at=material.created_at,
        updated_at=material.updated_at,
    )


def material_consumption_rule_response(
    rule: MaterialConsumptionRule,
) -> MaterialConsumptionRuleResponse:
    return MaterialConsumptionRuleResponse(
        id=rule.id,
        company_id=rule.company_id,
        material_id=rule.material_id,
        engine_type=rule.engine_type,
        name=rule.name,
        input_unit=rule.input_unit,
        consumption_rate=rule.consumption_rate,
        waste_percentage=rule.waste_percentage,
        description=rule.description,
        archived_at=rule.archived_at,
        created_at=rule.created_at,
        updated_at=rule.updated_at,
    )


@router.post(
    "/material-categories",
    response_model=MaterialCategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_material_category(
    payload: MaterialCategoryCreate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> MaterialCategoryResponse:
    category = MaterialCategory(
        company_id=company.id,
        name=payload.name,
        description=payload.description,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return material_category_response(category)


@router.get("/material-categories", response_model=list[MaterialCategoryResponse])
def list_material_categories(
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> list[MaterialCategoryResponse]:
    categories = (
        db.query(MaterialCategory)
        .filter(
            MaterialCategory.company_id == company.id,
            MaterialCategory.archived_at.is_(None),
        )
        .order_by(MaterialCategory.created_at.asc())
        .all()
    )
    return [material_category_response(category) for category in categories]


@router.patch("/material-categories/{category_id}", response_model=MaterialCategoryResponse)
def update_material_category(
    category_id: str,
    payload: MaterialCategoryUpdate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> MaterialCategoryResponse:
    category = get_active_material_category_for_company(
        db,
        company_id=company.id,
        category_id=category_id,
    )
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    db.add(category)
    db.commit()
    db.refresh(category)
    return material_category_response(category)


@router.post("/material-categories/{category_id}/archive", response_model=MaterialCategoryResponse)
def archive_material_category_endpoint(
    category_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> MaterialCategoryResponse:
    category = get_active_material_category_for_company(
        db,
        company_id=company.id,
        category_id=category_id,
    )
    archive_material_category(category)
    db.add(category)
    db.commit()
    db.refresh(category)
    return material_category_response(category)


@router.post(
    "/material-manufacturers",
    response_model=MaterialManufacturerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_material_manufacturer(
    payload: MaterialManufacturerCreate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> MaterialManufacturerResponse:
    manufacturer = MaterialManufacturer(
        company_id=company.id,
        name=payload.name,
        website=payload.website,
        note=payload.note,
    )
    db.add(manufacturer)
    db.commit()
    db.refresh(manufacturer)
    return material_manufacturer_response(manufacturer)


@router.get("/material-manufacturers", response_model=list[MaterialManufacturerResponse])
def list_material_manufacturers(
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> list[MaterialManufacturerResponse]:
    manufacturers = (
        db.query(MaterialManufacturer)
        .filter(
            MaterialManufacturer.company_id == company.id,
            MaterialManufacturer.archived_at.is_(None),
        )
        .order_by(MaterialManufacturer.created_at.asc())
        .all()
    )
    return [material_manufacturer_response(manufacturer) for manufacturer in manufacturers]


@router.patch(
    "/material-manufacturers/{manufacturer_id}",
    response_model=MaterialManufacturerResponse,
)
def update_material_manufacturer(
    manufacturer_id: str,
    payload: MaterialManufacturerUpdate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> MaterialManufacturerResponse:
    manufacturer = get_active_material_manufacturer_for_company(
        db,
        company_id=company.id,
        manufacturer_id=manufacturer_id,
    )
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(manufacturer, field, value)
    db.add(manufacturer)
    db.commit()
    db.refresh(manufacturer)
    return material_manufacturer_response(manufacturer)


@router.post(
    "/material-manufacturers/{manufacturer_id}/archive",
    response_model=MaterialManufacturerResponse,
)
def archive_material_manufacturer_endpoint(
    manufacturer_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> MaterialManufacturerResponse:
    manufacturer = get_active_material_manufacturer_for_company(
        db,
        company_id=company.id,
        manufacturer_id=manufacturer_id,
    )
    archive_material_manufacturer(manufacturer)
    db.add(manufacturer)
    db.commit()
    db.refresh(manufacturer)
    return material_manufacturer_response(manufacturer)


@router.get("/material-units", response_model=list[MaterialUnitResponse])
def list_material_units(
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> list[MaterialUnitResponse]:
    created_defaults = ensure_default_material_units(db)
    if created_defaults:
        db.commit()
    units = (
        db.query(MaterialUnit)
        .filter(
            MaterialUnit.archived_at.is_(None),
            or_(
                MaterialUnit.company_id == company.id,
                MaterialUnit.company_id.is_(None),
            ),
        )
        .order_by(MaterialUnit.is_default.desc(), MaterialUnit.key.asc())
        .all()
    )
    return [material_unit_response(unit) for unit in units]


@router.post(
    "/material-units",
    response_model=MaterialUnitResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_material_unit(
    payload: MaterialUnitCreate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> MaterialUnitResponse:
    unit = MaterialUnit(
        company_id=company.id,
        key=payload.key,
        name=payload.name,
        description=payload.description,
        is_default=False,
    )
    db.add(unit)
    db.commit()
    db.refresh(unit)
    return material_unit_response(unit)


@router.post(
    "/materials",
    response_model=MaterialResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_material(
    payload: MaterialCreate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> MaterialResponse:
    validate_material_links(
        db,
        company_id=company.id,
        category_id=payload.category_id,
        manufacturer_id=payload.manufacturer_id,
        unit_id=payload.unit_id,
    )
    material = Material(
        company_id=company.id,
        name=payload.name,
        sku=payload.sku,
        description=payload.description,
        category_id=payload.category_id,
        manufacturer_id=payload.manufacturer_id,
        unit_id=payload.unit_id,
        coverage_value=payload.coverage_value,
        coverage_unit=payload.coverage_unit,
        package_quantity=payload.package_quantity,
        waste_percentage_default=payload.waste_percentage_default,
        is_active=payload.is_active,
    )
    db.add(material)
    db.commit()
    db.refresh(material)
    return material_response(material)


@router.get("/materials", response_model=list[MaterialResponse])
def list_materials(
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> list[MaterialResponse]:
    materials = (
        db.query(Material)
        .filter(
            Material.company_id == company.id,
            Material.archived_at.is_(None),
        )
        .order_by(Material.created_at.asc())
        .all()
    )
    return [material_response(material) for material in materials]


@router.get("/materials/{material_id}", response_model=MaterialResponse)
def read_material(
    material_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> MaterialResponse:
    material = get_active_material_for_company(
        db,
        company_id=company.id,
        material_id=material_id,
    )
    return material_response(material)


@router.patch("/materials/{material_id}", response_model=MaterialResponse)
def update_material(
    material_id: str,
    payload: MaterialUpdate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> MaterialResponse:
    material = get_active_material_for_company(
        db,
        company_id=company.id,
        material_id=material_id,
    )
    values = payload.model_dump(exclude_unset=True)
    if "unit_id" in values and values["unit_id"] is None:
        raise validation_error("Мерната единица е задолжителна.")
    if values.get("category_id") is not None:
        get_active_material_category_for_company(
            db,
            company_id=company.id,
            category_id=values["category_id"],
        )
    if values.get("manufacturer_id") is not None:
        get_active_material_manufacturer_for_company(
            db,
            company_id=company.id,
            manufacturer_id=values["manufacturer_id"],
        )
    if values.get("unit_id") is not None:
        get_active_material_unit_for_company(
            db,
            company_id=company.id,
            unit_id=values["unit_id"],
        )
    for field, value in values.items():
        setattr(material, field, value)
    db.add(material)
    db.commit()
    db.refresh(material)
    return material_response(material)


@router.post("/materials/{material_id}/archive", response_model=MaterialResponse)
def archive_material_endpoint(
    material_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> MaterialResponse:
    material = get_active_material_for_company(
        db,
        company_id=company.id,
        material_id=material_id,
    )
    archive_material(material)
    db.add(material)
    db.commit()
    db.refresh(material)
    return material_response(material)


@router.post(
    "/material-consumption-rules",
    response_model=MaterialConsumptionRuleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_material_consumption_rule(
    payload: MaterialConsumptionRuleCreate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> MaterialConsumptionRuleResponse:
    material = get_active_material_for_company(
        db,
        company_id=company.id,
        material_id=payload.material_id,
    )
    validate_material_engine_type(payload.engine_type)
    rule = MaterialConsumptionRule(
        company_id=company.id,
        material_id=material.id,
        engine_type=payload.engine_type,
        name=payload.name,
        input_unit=payload.input_unit,
        consumption_rate=payload.consumption_rate,
        waste_percentage=payload.waste_percentage,
        description=payload.description,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return material_consumption_rule_response(rule)


@router.get(
    "/material-consumption-rules",
    response_model=list[MaterialConsumptionRuleResponse],
)
def list_material_consumption_rules(
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> list[MaterialConsumptionRuleResponse]:
    rules = (
        db.query(MaterialConsumptionRule)
        .join(Material, MaterialConsumptionRule.material_id == Material.id)
        .filter(
            MaterialConsumptionRule.company_id == company.id,
            MaterialConsumptionRule.archived_at.is_(None),
            Material.company_id == company.id,
            Material.archived_at.is_(None),
        )
        .order_by(MaterialConsumptionRule.created_at.asc())
        .all()
    )
    return [material_consumption_rule_response(rule) for rule in rules]


@router.get(
    "/materials/{material_id}/consumption-rules",
    response_model=list[MaterialConsumptionRuleResponse],
)
def list_material_consumption_rules_for_material(
    material_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> list[MaterialConsumptionRuleResponse]:
    material = get_active_material_for_company(
        db,
        company_id=company.id,
        material_id=material_id,
    )
    rules = (
        db.query(MaterialConsumptionRule)
        .filter(
            MaterialConsumptionRule.company_id == company.id,
            MaterialConsumptionRule.material_id == material.id,
            MaterialConsumptionRule.archived_at.is_(None),
        )
        .order_by(MaterialConsumptionRule.created_at.asc())
        .all()
    )
    return [material_consumption_rule_response(rule) for rule in rules]


@router.patch(
    "/material-consumption-rules/{rule_id}",
    response_model=MaterialConsumptionRuleResponse,
)
def update_material_consumption_rule(
    rule_id: str,
    payload: MaterialConsumptionRuleUpdate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> MaterialConsumptionRuleResponse:
    rule = get_active_material_consumption_rule_for_company(
        db,
        company_id=company.id,
        rule_id=rule_id,
    )
    values = payload.model_dump(exclude_unset=True)
    if "material_id" in values and values["material_id"] is None:
        raise validation_error("Материјалот е задолжителен.")
    if "engine_type" in values and values["engine_type"] is None:
        raise validation_error("Типот на калкулатор е задолжителен.")
    if values.get("material_id") is not None:
        material = get_active_material_for_company(
            db,
            company_id=company.id,
            material_id=values["material_id"],
        )
        values["material_id"] = material.id
    if values.get("engine_type") is not None:
        validate_material_engine_type(values["engine_type"])
    for field, value in values.items():
        setattr(rule, field, value)
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return material_consumption_rule_response(rule)


@router.post(
    "/material-consumption-rules/{rule_id}/archive",
    response_model=MaterialConsumptionRuleResponse,
)
def archive_material_consumption_rule_endpoint(
    rule_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> MaterialConsumptionRuleResponse:
    rule = get_active_material_consumption_rule_for_company(
        db,
        company_id=company.id,
        rule_id=rule_id,
    )
    archive_material_consumption_rule(rule)
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return material_consumption_rule_response(rule)
