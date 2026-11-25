from datetime import timedelta

from sqlalchemy import select

from app.core.config import Settings, get_settings
from app.core.security import create_access_token
from app.models.demo_request import DemoRequest
from app.models.identity import User
from app.models.subscription import SubscriptionPlan
from app.services import demo_mail
from app.services.demo_requests import invitation_token, utc_now

BASE = "/api/v1/demo-requests"
REQUEST = {
    "name": "Demo Tester",
    "email": "Tester@example.test",
    "company_name": "Test Construction",
    "message": "Estimate workflow",
}
PASSWORD = "A-new-demo-password"


def configure(client, monkeypatch):
    settings = Settings(
        demo_requests_enabled=True,
        demo_public_url="https://buildiq.example.test",
        demo_reviewer_email="reviewer@example.test",
        demo_mail_host="127.0.0.1",
        demo_mail_security="loopback",
        demo_mail_sender="demo@example.test",
        demo_mail_username="demo@example.test",
        demo_mail_password="test-relay-password",
    )
    client.app.dependency_overrides[get_settings] = lambda: settings
    delivered = []
    monkeypatch.setattr(demo_mail, "send_message", lambda config, *args: delivered.append(args))
    return settings, delivered


def bearer(user_id, company_id):
    return {"Authorization": f"Bearer {create_access_token(user_id, company_id)}"}


def test_request_notification_approval_and_isolated_trial(client, db_session, seeded_identity, monkeypatch):
    settings, delivered = configure(client, monkeypatch)
    reviewer = db_session.get(User, seeded_identity["owner_user_id"])
    reviewer.is_hq_admin = True
    db_session.add(SubscriptionPlan(key="demo-trial", name="Demo", billing_period="trial"))
    db_session.commit()
    reviewer_headers = bearer(reviewer.id, reviewer.company_id)
    ordinary_headers = bearer(seeded_identity["other_user_id"], seeded_identity["other_company_id"])

    assert client.get(BASE + "/availability").json() == {"enabled": True}
    assert client.post(BASE, json=REQUEST).status_code == 202
    assert client.post(BASE, json=REQUEST | {"email": "tester@example.test"}).status_code == 202
    item = db_session.scalars(select(DemoRequest)).one()
    assert item.email == "tester@example.test"
    assert client.get(BASE).status_code == 401
    assert client.get(BASE, headers=ordinary_headers).status_code == 403

    demo_mail.dispatch_due_mail(db_session, settings)
    demo_mail.dispatch_due_mail(db_session, settings)
    assert len(delivered) == 1
    assert delivered[0][0] == "reviewer@example.test"
    assert f"https://buildiq.example.test/admin/demo-requests/{item.id}" in delivered[0][2]
    assert client.get(f"{BASE}/{item.id}", headers=reviewer_headers).json()["message"] == REQUEST["message"]

    activation = {"token": invitation_token(settings, item), "password": PASSWORD}
    assert client.post(BASE + "/activate", json=activation).status_code == 400
    approve = f"{BASE}/{item.id}/approve"
    assert client.post(approve, headers=ordinary_headers).status_code == 403
    assert client.post(approve, headers=reviewer_headers).status_code == 200
    assert client.post(approve, headers=reviewer_headers).status_code == 200
    demo_mail.dispatch_due_mail(db_session, settings)
    demo_mail.dispatch_due_mail(db_session, settings)
    assert len(delivered) == 2
    assert delivered[1][0] == item.email
    assert f"/demo/activate#{activation['token']}" in delivered[1][2]
    assert "/login" in delivered[1][2]
    assert PASSWORD not in delivered[1][2]

    assert client.post(BASE + "/activate", json=activation).json() == {"email": item.email}
    assert client.post(BASE + "/activate", json=activation).status_code == 400
    login = client.post("/api/v1/auth/login", json={"email": item.email, "password": PASSWORD})
    assert login.status_code == 200
    demo_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    user = client.get("/api/v1/auth/me", headers=demo_headers).json()
    assert not user["is_hq_admin"]
    assert user["company_id"] not in [seeded_identity["demo_company_id"], seeded_identity["other_company_id"]]
    projects = client.get("/api/v1/projects", headers=demo_headers)
    assert projects.status_code == 200
    assert projects.json() == []
    assert client.get(BASE, headers=demo_headers).status_code == 403

    account = db_session.get(User, user["id"])
    account.access_expires_at = utc_now() - timedelta(seconds=1)
    db_session.commit()
    assert client.get("/api/v1/auth/me", headers=demo_headers).status_code == 401
    assert client.post("/api/v1/auth/login", json={"email": item.email, "password": PASSWORD}).status_code == 401


def test_existing_user_and_abuse_limits(client, db_session, seeded_identity, monkeypatch):
    settings, _ = configure(client, monkeypatch)
    assert client.post(BASE, json=REQUEST | {"email": seeded_identity["owner_email"]}).status_code == 202
    assert client.post(BASE, json=REQUEST | {"email": "a@example.test\r\nBcc: attacker@example.test"}).status_code == 422
    assert not db_session.scalars(select(DemoRequest)).all()
    for index in range(4):
        assert client.post(BASE, json=REQUEST | {"email": f"tester{index}@example.test"}).status_code == 202
    assert client.post(BASE, json=REQUEST).status_code == 429

    def unavailable(*args):
        raise OSError("synthetic SMTP failure")

    monkeypatch.setattr(demo_mail, "send_message", unavailable)
    demo_mail.dispatch_due_mail(db_session, settings)
    for item in db_session.scalars(select(DemoRequest)):
        assert item.email_attempts == 1
        assert item.notified_at is None
        assert item.next_email_at is not None


def test_configured_reviewer_can_approve_without_hq_role(client, db_session, seeded_identity, monkeypatch):
    settings, _ = configure(client, monkeypatch)
    settings.demo_approver_email = seeded_identity["owner_email"].upper()
    reviewer = db_session.get(User, seeded_identity["owner_user_id"])
    headers = bearer(reviewer.id, reviewer.company_id)
    assert client.post(BASE, json=REQUEST).status_code == 202
    item = db_session.scalars(select(DemoRequest)).one()

    profile = client.get("/api/v1/auth/me", headers=headers).json()
    assert profile["can_review_demo_requests"] is True
    assert profile["is_hq_admin"] is False
    assert client.post(f"{BASE}/{item.id}/approve", headers=headers).status_code == 200

    reviewer.access_expires_at = utc_now() + timedelta(days=1)
    db_session.commit()
    assert client.get("/api/v1/auth/me", headers=headers).json()["can_review_demo_requests"] is False
    assert client.get(BASE, headers=headers).status_code == 403
