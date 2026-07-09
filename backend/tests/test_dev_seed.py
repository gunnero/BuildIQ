from sqlalchemy.orm import Session

import app.seeds.dev as dev_seed
from app.models.calculation import CalculationRun
from app.models.customer import Customer, Property
from app.models.estimate import Estimate
from app.models.financial import Expense, Payment
from app.models.identity import Company, User
from app.models.material import Material
from app.models.measurement import Room, RoomOpening
from app.models.procurement import PriceBookItem, Supplier
from app.models.project import Project


def test_development_seed_creates_mvp_demo_flow(
    db_session: Session,
    monkeypatch,
) -> None:
    monkeypatch.setattr(dev_seed, "SessionLocal", lambda: db_session)

    dev_seed.seed_development_data()
    dev_seed.seed_development_data()

    company = db_session.query(Company).filter(Company.name == "Демо Градба").one()
    owner_user = db_session.query(User).filter(User.email == dev_seed.OWNER_EMAIL).one()
    assert owner_user.company_id == company.id
    assert owner_user.name == "Демо Сопственик"

    customer = db_session.query(Customer).filter(Customer.email == "aleksandar@example.test").one()
    property_record = db_session.query(Property).filter(Property.customer_id == customer.id).one()
    project = db_session.query(Project).filter(Project.property_id == property_record.id).one()
    room = db_session.query(Room).filter(Room.project_id == project.id).one()

    assert db_session.query(RoomOpening).filter(RoomOpening.room_id == room.id).count() == 2
    assert db_session.query(Material).filter(Material.company_id == project.company_id).count() == 1
    assert db_session.query(Supplier).filter(Supplier.company_id == project.company_id).count() == 1
    assert db_session.query(PriceBookItem).filter(PriceBookItem.company_id == project.company_id).count() == 1

    calculation = (
        db_session.query(CalculationRun)
        .filter(
            CalculationRun.company_id == project.company_id,
            CalculationRun.project_id == project.id,
            CalculationRun.room_id == room.id,
            CalculationRun.engine_type == "painting",
        )
        .one()
    )
    assert calculation.status == "completed"
    assert calculation.line_items

    estimate = (
        db_session.query(Estimate)
        .filter(Estimate.source_calculation_run_id == calculation.id)
        .one()
    )
    assert estimate.status == "accepted"
    assert estimate.revisions[0].items

    payment = db_session.query(Payment).filter(Payment.estimate_id == estimate.id).one()
    assert payment.status == "received"
    assert payment.amount > 0

    expense = db_session.query(Expense).filter(Expense.project_id == project.id).one()
    assert expense.status == "recorded"
    assert expense.amount > 0
