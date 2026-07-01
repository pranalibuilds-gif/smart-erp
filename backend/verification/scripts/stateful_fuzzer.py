import asyncio
import random
import uuid
from decimal import Decimal
from httpx import AsyncClient
from datetime import date

BASE_URL = "http://localhost:8000" # Assume app is running or use TestClient

class StatefulFuzzer:
    def __init__(self, client: AsyncClient, token: str, company_id: uuid.UUID):
        self.client = client
        self.headers = {"Authorization": f"Bearer {token}", "X-Company-ID": str(company_id)}
        self.company_id = company_id

        self.invoices = []
        self.transfers = []
        self.adjustments = []

        self.stock_items = []
        self.warehouses = []
        self.parties = []
        self.ledgers = []

    async def setup(self):
        # Fetch masters
        res = await self.client.get("/api/v1/masters/warehouses", headers=self.headers)
        self.warehouses = [w["id"] for w in res.json()["data"]]

        res = await self.client.get("/api/v1/masters/stock-items", headers=self.headers)
        self.stock_items = [i["id"] for i in res.json()["data"]]

        res = await self.client.get("/api/v1/parties", headers=self.headers)
        self.parties = [p["id"] for p in res.json()["data"]]

        res = await self.client.get("/api/v1/masters/ledgers", headers=self.headers)
        self.ledgers = [l["id"] for l in res.json()["data"]]

    async def run_random_op(self):
        ops = [
            self.op_create_invoice,
            self.op_post_invoice,
            self.op_cancel_invoice,
            self.op_create_transfer,
            self.op_post_transfer,
            self.op_cancel_transfer,
            # self.op_create_adjustment, # Skipped for brevity
        ]
        op = random.choice(ops)
        await op()

    async def op_create_invoice(self):
        if not self.parties or not self.stock_items or not self.warehouses: return
        payload = {
            "party_id": random.choice(self.parties),
            "document_type": random.choice(["SALES", "PURCHASE"]),
            "invoice_date": str(date.today()),
            "items": [{
                "stock_item_id": random.choice(self.stock_items),
                "warehouse_id": random.choice(self.warehouses),
                "item_name": "Fuzz Item",
                "quantity": random.randint(1, 10),
                "rate": random.randint(10, 100),
                "tax_rate": 0
            }]
        }
        res = await self.client.post("/api/v1/billing/invoices", json=payload, headers=self.headers)
        if res.status_code == 201:
            self.invoices.append(res.json()["data"]["id"])

    async def op_post_invoice(self):
        if not self.invoices: return
        inv_id = random.choice(self.invoices)
        await self.client.post(f"/api/v1/billing/invoices/{inv_id}/post", headers=self.headers)

    async def op_cancel_invoice(self):
        if not self.invoices: return
        inv_id = random.choice(self.invoices)
        await self.client.post(f"/api/v1/billing/invoices/{inv_id}/cancel", headers=self.headers)

    async def op_create_transfer(self):
        if len(self.warehouses) < 2 or not self.stock_items: return
        w1, w2 = random.sample(self.warehouses, 2)
        payload = {
            "from_warehouse_id": w1,
            "to_warehouse_id": w2,
            "transfer_date": str(date.today()),
            "items": [{"stock_item_id": random.choice(self.stock_items), "quantity": random.randint(1, 5)}]
        }
        res = await self.client.post("/api/v1/inventory/transfers", json=payload, headers=self.headers)
        if res.status_code == 201:
            self.transfers.append(res.json()["data"]["id"])

    async def op_post_transfer(self):
        if not self.transfers: return
        t_id = random.choice(self.transfers)
        await self.client.post(f"/api/v1/inventory/transfers/{t_id}/post", headers=self.headers)

    async def op_cancel_transfer(self):
        if not self.transfers: return
        t_id = random.choice(self.transfers)
        await self.client.post(f"/api/v1/inventory/transfers/{t_id}/cancel", headers=self.headers)

# Since running a real server and script is complex in this environment,
# I'll convert this to a pytest test that uses the existing fixtures.
