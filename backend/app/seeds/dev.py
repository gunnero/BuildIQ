import os
from datetime import date, datetime

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.customer import Customer, Property, PropertyNote
from app.models.identity import Company, Permission, Role, RolePermission, User, UserRole
from app.models.kernel import AuditLog, FeatureFlag
from app.models.material import Material, MaterialCategory, MaterialUnit
from app.models.measurement import Room, RoomOpening
from app.models.procurement import PriceBook, PriceBookItem, Supplier
from app.models.project import Project, ProjectStatusHistory, ProjectTimelineEvent
from app.schemas.calculation import CalculationRunCreate
from app.schemas.estimate import EstimateFromCalculationCreate
from app.schemas.financial import ExpenseCreate, PaymentCreate
from app.models.subscription import Subscription, SubscriptionPlan
from app.models.calculation import CalculationRun
from app.models.estimate import Estimate
from app.models.financial import Expense, ExpenseCategory, Payment
from app.services.calculations import execute_calculation_run
from app.services.estimates import change_estimate_status, create_estimate_from_calculation
from app.services.financial import create_expense_record, create_payment_record
from app.services.materials import ensure_default_material_units

HQ_EMAIL = "hq@buildiq.local"
OWNER_EMAIL = "owner@demo.buildiq.local"
DEFAULT_PASSWORD = "ChangeMe123!"


def get_or_create_company(
    db: Session,
    name: str,
    *,
    is_internal: bool = False,
) -> Company:
    company = db.query(Company).filter(Company.name == name).one_or_none()
    if company is not None:
        return company

    company = Company(name=name, status="active", is_internal=is_internal)
    db.add(company)
    db.flush()
    return company


def get_or_create_user(
    db: Session,
    *,
    company_id: str,
    name: str,
    email: str,
    password: str,
    is_hq_admin: bool = False,
) -> User:
    user = db.query(User).filter(User.email == email).one_or_none()
    if user is not None:
        return user

    user = User(
        company_id=company_id,
        name=name,
        email=email,
        password_hash=hash_password(password),
        status="active",
        is_hq_admin=is_hq_admin,
    )
    db.add(user)
    db.flush()
    return user


def get_or_create_permission(db: Session, key: str, name: str) -> Permission:
    permission = db.query(Permission).filter(Permission.key == key).one_or_none()
    if permission is not None:
        return permission

    permission = Permission(key=key, name=name)
    db.add(permission)
    db.flush()
    return permission


def get_or_create_role(
    db: Session,
    *,
    company_id: str,
    key: str,
    name: str,
) -> Role:
    role = (
        db.query(Role)
        .filter(Role.company_id == company_id, Role.key == key)
        .one_or_none()
    )
    if role is not None:
        return role

    role = Role(company_id=company_id, key=key, name=name, is_system_role=True)
    db.add(role)
    db.flush()
    return role


def ensure_user_role(db: Session, user: User, role: Role) -> None:
    exists = (
        db.query(UserRole)
        .filter(UserRole.user_id == user.id, UserRole.role_id == role.id)
        .one_or_none()
    )
    if exists is None:
        db.add(UserRole(user_id=user.id, role_id=role.id))


def ensure_role_permission(db: Session, role: Role, permission: Permission) -> None:
    exists = (
        db.query(RolePermission)
        .filter(
            RolePermission.role_id == role.id,
            RolePermission.permission_id == permission.id,
        )
        .one_or_none()
    )
    if exists is None:
        db.add(RolePermission(role_id=role.id, permission_id=permission.id))


def get_or_create_plan(db: Session) -> SubscriptionPlan:
    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.key == "starter").one_or_none()
    if plan is not None:
        return plan

    plan = SubscriptionPlan(
        key="starter",
        name="Starter",
        price_mkd=0,
        billing_period="monthly",
        is_active=True,
    )
    db.add(plan)
    db.flush()
    return plan


def ensure_subscription(db: Session, company: Company, plan: SubscriptionPlan) -> None:
    subscription = (
        db.query(Subscription)
        .filter(Subscription.company_id == company.id, Subscription.plan_id == plan.id)
        .one_or_none()
    )
    if subscription is None:
        db.add(Subscription(company_id=company.id, plan_id=plan.id, status="active"))


def ensure_feature_flag(db: Session) -> None:
    feature_flag = (
        db.query(FeatureFlag)
        .filter(FeatureFlag.key == "identity.tenant_foundation")
        .one_or_none()
    )
    if feature_flag is None:
        db.add(
            FeatureFlag(
                key="identity.tenant_foundation",
                name="Identity and Tenant Foundation",
                default_enabled=True,
            )
        )


def get_or_create_customer(db: Session, *, company_id: str) -> Customer:
    customer = (
        db.query(Customer)
        .filter(Customer.company_id == company_id, Customer.email == "aleksandar@example.test")
        .one_or_none()
    )
    if customer is None:
        customer = Customer(
            company_id=company_id,
            name="Александар Петровски",
            phone="+38970111222",
            email="aleksandar@example.test",
            address="ул. Македонија 12, Скопје",
            note="Demo customer for the local MVP flow.",
            status="active",
        )
        db.add(customer)
        db.flush()
    return customer


def get_or_create_property(db: Session, *, company_id: str, customer: Customer) -> Property:
    property_record = (
        db.query(Property)
        .filter(
            Property.company_id == company_id,
            Property.customer_id == customer.id,
            Property.name == "Стан Центар",
        )
        .one_or_none()
    )
    if property_record is None:
        property_record = Property(
            company_id=company_id,
            customer_id=customer.id,
            name="Стан Центар",
            address="ул. Македонија 12",
            city="Скопје",
            note="Demo apartment used for the MVP walkthrough.",
            status="active",
        )
        db.add(property_record)
        db.flush()
        db.add(
            PropertyNote(
                company_id=company_id,
                property_id=property_record.id,
                content="Демо белешка: бојадисување на дневна соба.",
            )
        )
    return property_record


def get_or_create_project(
    db: Session,
    *,
    company_id: str,
    customer: Customer,
    property_record: Property,
    owner_user: User,
) -> Project:
    project = (
        db.query(Project)
        .filter(
            Project.company_id == company_id,
            Project.customer_id == customer.id,
            Project.property_id == property_record.id,
            Project.name == "Бојадисување стан Центар",
        )
        .one_or_none()
    )
    if project is None:
        project = Project(
            company_id=company_id,
            customer_id=customer.id,
            property_id=property_record.id,
            name="Бојадисување стан Центар",
            description="Demo MVP painting project.",
            address=property_record.address,
            status="active",
            agreed_project_price=40000,
            start_date=date(2026, 7, 1),
            due_date=date(2026, 7, 15),
        )
        db.add(project)
        db.flush()
        now = datetime.utcnow()
        db.add(
            ProjectStatusHistory(
                company_id=company_id,
                project_id=project.id,
                from_status=None,
                to_status="active",
                note="Demo project seeded for local MVP walkthrough.",
                changed_by_user_id=owner_user.id,
                created_at=now,
            )
        )
        db.add(
            ProjectTimelineEvent(
                company_id=company_id,
                project_id=project.id,
                event_type="created",
                message="Demo project created by the local seed command.",
                created_by_user_id=owner_user.id,
                created_at=now,
            )
        )
    return project


def get_or_create_demo_room(db: Session, *, company_id: str, project: Project) -> Room:
    room = (
        db.query(Room)
        .filter(
            Room.company_id == company_id,
            Room.project_id == project.id,
            Room.name == "Дневна соба",
        )
        .one_or_none()
    )
    if room is None:
        room = Room(
            company_id=company_id,
            project_id=project.id,
            name="Дневна соба",
            room_type="living_room",
            floor="1",
            note="Demo room with one door and two windows.",
            length=5.0,
            width=4.0,
            height=2.7,
        )
        db.add(room)
        db.flush()
    openings = {
        "Врата": {"opening_type": "door", "width": 0.9, "height": 2.05, "quantity": 1},
        "Прозорци": {"opening_type": "window", "width": 1.4, "height": 1.2, "quantity": 2},
    }
    for name, values in openings.items():
        exists = (
            db.query(RoomOpening)
            .filter(
                RoomOpening.company_id == company_id,
                RoomOpening.room_id == room.id,
                RoomOpening.name == name,
            )
            .one_or_none()
        )
        if exists is None:
            db.add(RoomOpening(company_id=company_id, room_id=room.id, name=name, **values))
    db.flush()
    return room


def get_or_create_paint_material(db: Session, *, company_id: str) -> Material:
    ensure_default_material_units(db)
    liter_unit = (
        db.query(MaterialUnit)
        .filter(MaterialUnit.company_id.is_(None), MaterialUnit.key == "liter")
        .one()
    )
    category = (
        db.query(MaterialCategory)
        .filter(MaterialCategory.company_id == company_id, MaterialCategory.name == "Бои")
        .one_or_none()
    )
    if category is None:
        category = MaterialCategory(
            company_id=company_id,
            name="Бои",
            description="Demo paint materials.",
        )
        db.add(category)
        db.flush()

    material = (
        db.query(Material)
        .filter(Material.company_id == company_id, Material.sku == "DEMO-PAINT-WHITE")
        .one_or_none()
    )
    if material is None:
        material = Material(
            company_id=company_id,
            name="Внатрешна бела боја",
            sku="DEMO-PAINT-WHITE",
            description="Demo paint with m2/liter coverage.",
            category_id=category.id,
            unit_id=liter_unit.id,
            coverage_value=10.0,
            coverage_unit="m2/liter",
            package_quantity=10.0,
            waste_percentage_default=10.0,
            is_active=True,
        )
        db.add(material)
        db.flush()
    return material


def get_or_create_supplier(db: Session, *, company_id: str) -> Supplier:
    supplier = (
        db.query(Supplier)
        .filter(Supplier.company_id == company_id, Supplier.name == "Демо Маркет Материјали")
        .one_or_none()
    )
    if supplier is None:
        supplier = Supplier(
            company_id=company_id,
            name="Демо Маркет Материјали",
            supplier_type="store",
            phone="+38970111333",
            email="supplier@example.test",
            address="бул. Партизански Одреди 20, Скопје",
            note="Demo supplier for local MVP data.",
            status="active",
        )
        db.add(supplier)
        db.flush()
    return supplier


def ensure_price_book_item(
    db: Session,
    *,
    company_id: str,
    supplier: Supplier,
    material: Material,
) -> PriceBookItem:
    price_book = (
        db.query(PriceBook)
        .filter(
            PriceBook.company_id == company_id,
            PriceBook.supplier_id == supplier.id,
            PriceBook.name == "Демо малопродажен ценовник",
        )
        .one_or_none()
    )
    if price_book is None:
        price_book = PriceBook(
            company_id=company_id,
            supplier_id=supplier.id,
            name="Демо малопродажен ценовник",
            price_type="retail",
            status="active",
            currency="MKD",
            valid_from=date(2026, 1, 1),
            notes="Demo retail price book for MVP walkthrough.",
        )
        db.add(price_book)
        db.flush()

    item = (
        db.query(PriceBookItem)
        .filter(
            PriceBookItem.company_id == company_id,
            PriceBookItem.price_book_id == price_book.id,
            PriceBookItem.material_id == material.id,
        )
        .one_or_none()
    )
    if item is None:
        item = PriceBookItem(
            company_id=company_id,
            price_book_id=price_book.id,
            material_id=material.id,
            supplier_id=supplier.id,
            supplier_sku="SUP-DEMO-PAINT-WHITE",
            unit_price=450.0,
            currency="MKD",
            valid_from=date(2026, 1, 1),
            notes="Demo price per liter.",
        )
        db.add(item)
        db.flush()
    return item


def get_or_create_painting_calculation(
    db: Session,
    *,
    company_id: str,
    owner_user: User,
    project: Project,
    room: Room,
    material: Material,
) -> CalculationRun:
    calculation = (
        db.query(CalculationRun)
        .filter(
            CalculationRun.company_id == company_id,
            CalculationRun.project_id == project.id,
            CalculationRun.room_id == room.id,
            CalculationRun.engine_type == "painting",
            CalculationRun.status == "completed",
        )
        .one_or_none()
    )
    if calculation is not None:
        return calculation

    calculation_payload = CalculationRunCreate(
        engine_type="painting",
        project_id=project.id,
        room_id=room.id,
        input_payload={
            "include_walls": True,
            "include_ceiling": True,
            "coats": 2,
            "primer_coats": 0,
            "paint_material_id": material.id,
            "waste_percentage": 10,
            "labor_rate_per_m2": 520,
            "notes": "Demo painting calculation for the MVP walkthrough.",
        },
    )
    calculation = execute_calculation_run(
        db,
        company_id=company_id,
        created_by_user_id=owner_user.id,
        payload=calculation_payload,
    )
    db.flush()
    return calculation


def get_or_create_estimate_from_calculation(
    db: Session,
    *,
    company_id: str,
    calculation: CalculationRun,
) -> Estimate:
    estimate = (
        db.query(Estimate)
        .filter(
            Estimate.company_id == company_id,
            Estimate.source_calculation_run_id == calculation.id,
        )
        .one_or_none()
    )
    if estimate is None:
        estimate = create_estimate_from_calculation(
            db,
            company_id=company_id,
            calculation_run_id=calculation.id,
            payload=EstimateFromCalculationCreate(
                title="Понуда за бојадисување",
                description="Demo estimate copied from a completed painting calculation.",
            ),
        )
        db.flush()
    if estimate.status not in {"accepted", "archived"}:
        change_estimate_status(estimate, status_value="accepted")
        db.flush()
    return estimate


def get_or_create_payment(
    db: Session,
    *,
    company_id: str,
    owner_user: User,
    customer: Customer,
    project: Project,
    estimate: Estimate,
) -> Payment:
    payment = (
        db.query(Payment)
        .filter(
            Payment.company_id == company_id,
            Payment.project_id == project.id,
            Payment.estimate_id == estimate.id,
            Payment.note == "Demo received payment.",
        )
        .one_or_none()
    )
    if payment is None:
        payment = create_payment_record(
            db,
            company_id=company_id,
            user_id=owner_user.id,
            payload=PaymentCreate(
                customer_id=customer.id,
                project_id=project.id,
                estimate_id=estimate.id,
                amount=20000.0,
                payment_method="bank_transfer",
                payment_date=date(2026, 7, 3),
                status="received",
                note="Demo received payment.",
            ),
        )
        db.flush()
    return payment


def get_or_create_expense(
    db: Session,
    *,
    company_id: str,
    owner_user: User,
    project: Project,
    supplier: Supplier,
    material: Material,
) -> Expense:
    category = (
        db.query(ExpenseCategory)
        .filter(ExpenseCategory.company_id == company_id, ExpenseCategory.name == "Материјали")
        .one_or_none()
    )
    if category is None:
        category = ExpenseCategory(
            company_id=company_id,
            name="Материјали",
            description="Demo material expenses.",
        )
        db.add(category)
        db.flush()

    expense = (
        db.query(Expense)
        .filter(
            Expense.company_id == company_id,
            Expense.project_id == project.id,
            Expense.description == "Демо набавка на боја",
        )
        .one_or_none()
    )
    if expense is None:
        expense = create_expense_record(
            db,
            company_id=company_id,
            user_id=owner_user.id,
            payload=ExpenseCreate(
                project_id=project.id,
                category_id=category.id,
                supplier_id=supplier.id,
                material_id=material.id,
                description="Демо набавка на боја",
                amount=7000.0,
                expense_date=date(2026, 7, 2),
                payment_method="cash",
                status="recorded",
                note="Demo expense for MVP walkthrough.",
            ),
        )
        db.flush()
    return expense


def ensure_mvp_demo_data(db: Session, *, demo_company: Company, owner_user: User) -> None:
    customer = get_or_create_customer(db, company_id=demo_company.id)
    property_record = get_or_create_property(
        db,
        company_id=demo_company.id,
        customer=customer,
    )
    project = get_or_create_project(
        db,
        company_id=demo_company.id,
        customer=customer,
        property_record=property_record,
        owner_user=owner_user,
    )
    room = get_or_create_demo_room(db, company_id=demo_company.id, project=project)
    material = get_or_create_paint_material(db, company_id=demo_company.id)
    supplier = get_or_create_supplier(db, company_id=demo_company.id)
    ensure_price_book_item(
        db,
        company_id=demo_company.id,
        supplier=supplier,
        material=material,
    )
    calculation = get_or_create_painting_calculation(
        db,
        company_id=demo_company.id,
        owner_user=owner_user,
        project=project,
        room=room,
        material=material,
    )
    estimate = get_or_create_estimate_from_calculation(
        db,
        company_id=demo_company.id,
        calculation=calculation,
    )
    get_or_create_payment(
        db,
        company_id=demo_company.id,
        owner_user=owner_user,
        customer=customer,
        project=project,
        estimate=estimate,
    )
    get_or_create_expense(
        db,
        company_id=demo_company.id,
        owner_user=owner_user,
        project=project,
        supplier=supplier,
        material=material,
    )


def seed_development_data() -> None:
    hq_password = os.getenv("BUILDIQ_SEED_HQ_PASSWORD", DEFAULT_PASSWORD)
    owner_password = os.getenv("BUILDIQ_SEED_OWNER_PASSWORD", DEFAULT_PASSWORD)

    db = SessionLocal()
    try:
        hq_company = get_or_create_company(db, "BuildIQ HQ", is_internal=True)
        demo_company = get_or_create_company(db, "Demo Build Company")

        get_or_create_user(
            db,
            company_id=hq_company.id,
            name="BuildIQ HQ Admin",
            email=HQ_EMAIL,
            password=hq_password,
            is_hq_admin=True,
        )
        owner_user = get_or_create_user(
            db,
            company_id=demo_company.id,
            name="Demo Owner",
            email=OWNER_EMAIL,
            password=owner_password,
        )

        roles = {
            "owner": get_or_create_role(db, company_id=demo_company.id, key="owner", name="Owner"),
            "manager": get_or_create_role(db, company_id=demo_company.id, key="manager", name="Manager"),
            "worker": get_or_create_role(db, company_id=demo_company.id, key="worker", name="Worker"),
        }

        permissions = [
            get_or_create_permission(db, "company:read", "Read company"),
            get_or_create_permission(db, "subscription:read", "Read subscription"),
            get_or_create_permission(db, "users:manage", "Manage users"),
        ]
        for permission in permissions:
            ensure_role_permission(db, roles["owner"], permission)
        ensure_user_role(db, owner_user, roles["owner"])

        plan = get_or_create_plan(db)
        ensure_subscription(db, demo_company, plan)
        ensure_feature_flag(db)
        ensure_mvp_demo_data(db, demo_company=demo_company, owner_user=owner_user)

        db.add(
            AuditLog(
                company_id=demo_company.id,
                acting_user_id=owner_user.id,
                entity_type="development_seed",
                entity_id=demo_company.id,
                action="seeded",
            )
        )
        db.commit()
    finally:
        db.close()

    print("Development seed data ready.")
    print("MVP demo data ready.")
    print(f"HQ admin: {HQ_EMAIL}")
    print(f"Demo owner: {OWNER_EMAIL}")


def main() -> None:
    seed_development_data()


if __name__ == "__main__":
    main()
