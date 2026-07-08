from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.calculations import router as calculations_router
from app.api.v1.companies import router as companies_router
from app.api.v1.customers import router as customers_router
from app.api.v1.health import router as health_router
from app.api.v1.materials import router as materials_router
from app.api.v1.measurements import router as measurements_router
from app.api.v1.projects import router as projects_router
from app.api.v1.properties import router as properties_router
from app.api.v1.rooms import router as rooms_router
from app.api.v1.subscription import router as subscription_router
from app.api.v1.tasks import router as tasks_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(calculations_router)
api_router.include_router(companies_router)
api_router.include_router(customers_router)
api_router.include_router(health_router)
api_router.include_router(materials_router)
api_router.include_router(measurements_router)
api_router.include_router(projects_router)
api_router.include_router(properties_router)
api_router.include_router(rooms_router)
api_router.include_router(subscription_router)
api_router.include_router(tasks_router)
