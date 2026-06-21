from pydantic import BaseModel


class DashboardMetrics(BaseModel):
    total_sales: float
    total_purchases: float
    total_receivables: float
    total_payables: float
    inventory_value: float
