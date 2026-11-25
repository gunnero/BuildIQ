from datetime import timedelta
from email.message import EmailMessage
import logging
import smtplib
import ssl

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models.demo_request import DemoRequest
from app.services.demo_requests import INVITE_LIFETIME, as_utc, invitation_token, utc_now

logger = logging.getLogger(__name__)


def send_message(settings: Settings, recipient: str, subject: str, body: str) -> None:
    message = EmailMessage()
    message["From"] = settings.demo_mail_sender
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)
    context = ssl.create_default_context()
    args = (settings.demo_mail_host, settings.demo_mail_port)
    smtp = (smtplib.SMTP_SSL(*args, timeout=10, context=context)
            if settings.demo_mail_security == "tls" else smtplib.SMTP(*args, timeout=10))
    try:
        if settings.demo_mail_security == "starttls":
            smtp.starttls(context=context)
        smtp.login(settings.demo_mail_username, settings.demo_mail_password.get_secret_value())
        smtp.send_message(message, from_addr=settings.demo_mail_sender, to_addrs=[recipient])
    finally:
        try:
            smtp.close()
        except OSError:
            pass


def dispatch_due_mail(db: Session, settings: Settings, limit: int = 20) -> None:
    if not settings.demo_requests_enabled:
        return
    origin = settings.demo_public_url.rstrip("/")
    for _ in range(limit):
        now = utc_now()
        item = db.scalar(
            select(DemoRequest).where(DemoRequest.next_email_at <= now)
            .order_by(DemoRequest.next_email_at, DemoRequest.id)
            .limit(1).with_for_update(skip_locked=True)
        )
        if item is None:
            db.rollback()
            return

        approved = item.approved_at is not None
        if approved and as_utc(item.approved_at) + INVITE_LIFETIME <= now:
            item.next_email_at = None
            db.commit()
            continue
        if approved:
            recipient = item.email
            subject = "BuildIQ — вашиот демо пристап е одобрен"
            setup_url = f"{origin}/demo/activate#{invitation_token(settings, item)}"
            body = (
                f"Демо пристапот за {item.email} е одобрен.\n\n"
                f"Поставете лозинка во следните 7 дена:\n{setup_url}\n\n"
                f"Потоа најавете се со {item.email}:\n{origin}/login\n\n"
                f"Тестирајте проекти: {origin}/projects\n"
                f"Тестирајте пресметки: {origin}/calculations\n\n"
                "Демо работниот простор е достапен 14 дена по активацијата. "
                "За тестирање користете примерни податоци."
            )
        else:
            recipient = settings.demo_reviewer_email
            subject = "BuildIQ — ново барање за демо"
            body = (
                "Примено е ново барање за демо на BuildIQ.\n\n"
                f"Најавете се за да го прегледате и одобрите:\n{origin}/admin/demo-requests/{item.id}"
            )
        try:
            send_message(settings, recipient, subject, body)
        except (OSError, smtplib.SMTPException) as error:
            item.email_attempts += 1
            delay = min(2 ** min(item.email_attempts, 6), 60)
            item.next_email_at = now + timedelta(minutes=delay)
            logger.warning("Demo mail delivery failed for request %s (%s)", item.id, type(error).__name__)
        else:
            if approved:
                item.invitation_sent_at = now
            else:
                item.notified_at = now
            item.next_email_at = None
            item.email_attempts = 0
        db.commit()
