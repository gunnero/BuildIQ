from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.companies import router as companies_router
from app.api.v1.customers import router as customers_router
from app.api.v1.health import router as health_router
from app.api.v1.properties import router as properties_router
from app.api.v1.subscription import router as subscription_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(companies_router)
api_router.include_router(customers_router)
api_router.include_router(health_router)
api_router.include_router(properties_router)
api_router.include_router(subscription_router)
