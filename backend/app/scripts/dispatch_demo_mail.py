from app.core.config import get_settings
from app.db.session import SessionLocal
from app.services.demo_mail import dispatch_due_mail


def main() -> None:
    with SessionLocal() as db:
        dispatch_due_mail(db, get_settings())


if __name__ == "__main__":
    main()
