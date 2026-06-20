from fastapi import APIRouter
from app.api.v1.endpoints import health
from app.modules.auth.router import router as auth_router
from app.modules.companies.router import router as companies_router
from app.modules.masters.router import router as masters_router
from app.modules.parties.router import router as parties_router

api_v1_router = APIRouter()

api_v1_router.include_router(health.router, tags=["Health"])
api_v1_router.include_router(auth_router)
api_v1_router.include_router(companies_router)
api_v1_router.include_router(masters_router)
api_v1_router.include_router(parties_router)
