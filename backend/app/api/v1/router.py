from fastapi import APIRouter
from app.api.v1.endpoints import health
from app.modules.auth.router import router as auth_router
from app.modules.companies.router import router as companies_router
from app.modules.masters.router import router as masters_router
from app.modules.parties.router import router as parties_router
from app.modules.vouchers.router import router as vouchers_router
from app.modules.billing.router import router as billing_router
from app.modules.reports.router import router as reports_router
from app.modules.audit.router import router as audit_router
from app.modules.inventory.router import router as inventory_router
from app.modules.banking.router import router as banking_router
from app.modules.notifications.router import router as notifications_router
from app.modules.search.router import router as search_router

api_v1_router = APIRouter()

api_v1_router.include_router(health.router, tags=["Health"])
api_v1_router.include_router(auth_router)
api_v1_router.include_router(companies_router)
api_v1_router.include_router(masters_router)
api_v1_router.include_router(parties_router)
api_v1_router.include_router(vouchers_router)
api_v1_router.include_router(billing_router)
api_v1_router.include_router(reports_router)
api_v1_router.include_router(audit_router)
api_v1_router.include_router(inventory_router)
api_v1_router.include_router(banking_router)
api_v1_router.include_router(notifications_router)
api_v1_router.include_router(search_router)
