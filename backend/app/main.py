from fastapi import FastAPI

from app.api.v1.health import router as health_router
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging

OPENAPI_TAGS = [
    {"name": "health", "description": "Health checks."},
    {"name": "auth", "description": "Authentication and current user endpoints."},
    {"name": "companies", "description": "Current company endpoints."},
    {"name": "subscriptions", "description": "Current subscription endpoints."},
    {"name": "customers", "description": "Customer records and contacts."},
    {"name": "properties", "description": "Properties, contacts, and notes."},
    {"name": "projects", "description": "Project lifecycle endpoints."},
    {"name": "tasks", "description": "Project task endpoints."},
    {"name": "rooms", "description": "Room and opening endpoints."},
    {"name": "measurements", "description": "Measurement set and item endpoints."},
    {"name": "materials", "description": "Material catalog endpoints."},
    {"name": "procurement", "description": "Supplier, price book, and price resolution endpoints."},
    {"name": "calculations", "description": "Calculation engine endpoints."},
    {"name": "estimates", "description": "Estimate and revision endpoints."},
    {"name": "payments", "description": "Payment and project financial summary endpoints."},
    {"name": "expenses", "description": "Expense and expense category endpoints."},
]


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        openapi_tags=OPENAPI_TAGS,
    )
    app.include_router(health_router)
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
