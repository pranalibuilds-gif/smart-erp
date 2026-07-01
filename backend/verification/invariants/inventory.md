# Inventory Invariants

| Invariant | Rule | Enforcement |
| :--- | :--- | :--- |
| **Negative Stock Prevention** | Inventory quantities in any warehouse can never drop below zero. | `InventoryPostingService.post_inventory` |
| **Sub-ledger Traceability** | Every change to a cached stock quantity must be backed by an `InventoryTransaction`. | `InventoryPostingService.post_inventory`, `StockTransferService.post_transfer` |
| **WAC Accuracy** | Weighted Average Cost must be recomputed for every inward transaction. | `InventoryPostingService.post_inventory` |
| **Warehouse Distribution** | The sum of quantities across all warehouses must equal the Company-wide total. | `InventoryPostingService` (Atomic multi-table update) |
