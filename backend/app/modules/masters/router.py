import uuid
from typing import List
from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.database.session import get_db
from app.shared.schemas.responses import StandardResponse
from app.modules.auth.dependencies import get_current_user, get_current_company, PermissionRequired
from app.modules.auth.models import User
from app.modules.companies.models import Company
from .service import MastersService
from .schemas.account_groups import AccountGroupCreate, AccountGroupUpdate, AccountGroupRead
from .schemas.ledgers import LedgerCreate, LedgerUpdate, LedgerRead
from .schemas.units import UnitCreate, UnitUpdate, UnitRead
from .schemas.stock_groups import StockGroupCreate, StockGroupUpdate, StockGroupRead
from .schemas.stock_items import StockItemCreate, StockItemUpdate, StockItemRead
from .schemas.warehouses import WarehouseCreate, WarehouseUpdate, WarehouseRead

router = APIRouter(prefix="/masters", tags=["Masters"])

# --- Account Groups ---

@router.post("/account-groups", response_model=StandardResponse[AccountGroupRead], status_code=status.HTTP_201_CREATED)
async def create_account_group(
    data: AccountGroupCreate,
    current_user: User = Depends(get_current_user),
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    service = MastersService(db)
    group = await service.create_account_group(company.id, current_user.id, data)
    return StandardResponse(success=True, data=AccountGroupRead.model_validate(group), message="Account group created")


@router.get("/account-groups", response_model=StandardResponse[List[AccountGroupRead]])
async def list_account_groups(
    root_only: bool = Query(False),
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    service = MastersService(db)
    groups = await service.get_account_groups(company.id, root_only=root_only)
    return StandardResponse(success=True, data=[AccountGroupRead.model_validate(g) for g in groups])


@router.patch("/account-groups/{group_id}", response_model=StandardResponse[AccountGroupRead])
async def update_account_group(
    group_id: uuid.UUID,
    data: AccountGroupUpdate,
    current_user: User = Depends(get_current_user),
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    service = MastersService(db)
    group = await service.update_account_group(company.id, group_id, current_user.id, data)
    return StandardResponse(success=True, data=AccountGroupRead.model_validate(group))


@router.delete("/account-groups/{group_id}")
async def delete_account_group(
    group_id: uuid.UUID,
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    service = MastersService(db)
    await service.delete_account_group(company.id, group_id)
    return StandardResponse(success=True, message="Account group deleted")


# --- Ledgers ---

@router.post("/ledgers", response_model=StandardResponse[LedgerRead], status_code=status.HTTP_201_CREATED)
async def create_ledger(
    data: LedgerCreate,
    current_user: User = Depends(get_current_user),
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    service = MastersService(db)
    ledger = await service.create_ledger(company.id, current_user.id, data)
    return StandardResponse(success=True, data=LedgerRead.model_validate(ledger), message="Ledger created")


@router.get("/ledgers", response_model=StandardResponse[List[LedgerRead]])
async def list_ledgers(
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    service = MastersService(db)
    ledgers = await service.get_ledgers(company.id)
    return StandardResponse(success=True, data=[LedgerRead.model_validate(l) for l in ledgers])


@router.get("/ledgers/{ledger_id}", response_model=StandardResponse[LedgerRead])
async def get_ledger(
    ledger_id: uuid.UUID,
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    service = MastersService(db)
    ledger = await service.ledger_repo.get(ledger_id)
    if not ledger or ledger.company_id != company.id:
        raise HTTPException(status_code=404, detail="Ledger not found")
    return StandardResponse(success=True, data=LedgerRead.model_validate(ledger))


@router.patch("/ledgers/{ledger_id}", response_model=StandardResponse[LedgerRead])
async def update_ledger(
    ledger_id: uuid.UUID,
    data: LedgerUpdate,
    current_user: User = Depends(get_current_user),
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    service = MastersService(db)
    ledger = await service.update_ledger(company.id, ledger_id, current_user.id, data)
    return StandardResponse(success=True, data=LedgerRead.model_validate(ledger))


# --- Units ---

@router.post("/units", response_model=StandardResponse[UnitRead], status_code=status.HTTP_201_CREATED)
async def create_unit(
    data: UnitCreate,
    current_user: User = Depends(get_current_user),
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    service = MastersService(db)
    unit = await service.create_unit(company.id, current_user.id, data)
    return StandardResponse(success=True, data=UnitRead.model_validate(unit), message="Unit created")


@router.get("/units", response_model=StandardResponse[List[UnitRead]])
async def list_units(
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    service = MastersService(db)
    units = await service.get_units(company.id)
    return StandardResponse(success=True, data=[UnitRead.model_validate(u) for u in units])


@router.patch("/units/{unit_id}", response_model=StandardResponse[UnitRead])
async def update_unit(
    unit_id: uuid.UUID,
    data: UnitUpdate,
    current_user: User = Depends(get_current_user),
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    service = MastersService(db)
    unit = await service.update_unit(company.id, unit_id, current_user.id, data)
    return StandardResponse(success=True, data=UnitRead.model_validate(unit))


@router.delete("/units/{unit_id}")
async def delete_unit(
    unit_id: uuid.UUID,
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    service = MastersService(db)
    await service.delete_unit(company.id, unit_id)
    return StandardResponse(success=True, message="Unit deleted")


# --- Stock Groups ---

@router.post("/stock-groups", response_model=StandardResponse[StockGroupRead], status_code=status.HTTP_201_CREATED)
async def create_stock_group(
    data: StockGroupCreate,
    current_user: User = Depends(get_current_user),
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    service = MastersService(db)
    group = await service.create_stock_group(company.id, current_user.id, data)
    return StandardResponse(success=True, data=StockGroupRead.model_validate(group), message="Stock group created")


@router.get("/stock-groups", response_model=StandardResponse[List[StockGroupRead]])
async def list_stock_groups(
    root_only: bool = Query(False),
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    service = MastersService(db)
    groups = await service.get_stock_groups(company.id, root_only=root_only)
    return StandardResponse(success=True, data=[StockGroupRead.model_validate(g) for g in groups])


# --- Stock Items ---

@router.post("/stock-items", response_model=StandardResponse[StockItemRead], status_code=status.HTTP_201_CREATED)
async def create_stock_item(
    data: StockItemCreate,
    current_user: User = Depends(get_current_user),
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    service = MastersService(db)
    item = await service.create_stock_item(company.id, current_user.id, data)
    return StandardResponse(success=True, data=StockItemRead.model_validate(item), message="Stock item created")


@router.get("/stock-items", response_model=StandardResponse[List[StockItemRead]])
async def list_stock_items(
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    service = MastersService(db)
    items = await service.get_stock_items(company.id)
    return StandardResponse(success=True, data=[StockItemRead.model_validate(i) for i in items])


# --- Warehouses ---

@router.post("/warehouses", response_model=StandardResponse[WarehouseRead], status_code=status.HTTP_201_CREATED)
async def create_warehouse(
    data: WarehouseCreate,
    current_user: User = Depends(get_current_user),
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    service = MastersService(db)
    warehouse = await service.create_warehouse(company.id, current_user.id, data)
    return StandardResponse(success=True, data=WarehouseRead.model_validate(warehouse), message="Warehouse created")


@router.get("/warehouses", response_model=StandardResponse[List[WarehouseRead]])
async def list_warehouses(
    company: Company = Depends(get_current_company),
    db: AsyncSession = Depends(get_db)
):
    service = MastersService(db)
    warehouses = await service.list_warehouses(company.id)
    return StandardResponse(success=True, data=[WarehouseRead.model_validate(w) for w in warehouses])
