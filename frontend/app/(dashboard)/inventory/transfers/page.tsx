"use client";

import { useEffect, useState } from "react";
import { listTransfers, StockTransfer } from "@/features/inventory/api/inventory-api";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Plus, Eye } from "lucide-react";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { useMasterStore } from "@/stores/master-store";

export default function StockTransfersPage() {
  const [items, setItems] = useState<StockTransfer[]>([]);
  const [loading, setLoading] = useState(true);
  const { warehouses, fetchMasters } = useMasterStore();

  useEffect(() => {
    fetchMasters();
    listTransfers().then(setItems).finally(() => setLoading(false));
  }, [fetchMasters]);

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold">Stock Transfers</h1>
        <Button asChild>
          <Link href="/inventory/transfers/new">
            <Plus className="mr-2 h-4 w-4" /> New Transfer
          </Link>
        </Button>
      </div>

      {loading ? <div>Loading...</div> : (
        <div className="bg-white border rounded-lg overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Number</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>From</TableHead>
                <TableHead>To</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {items.map((item) => (
                <TableRow key={item.id}>
                  <TableCell className="font-medium">{item.transfer_no}</TableCell>
                  <TableCell>{item.transfer_date}</TableCell>
                  <TableCell>{warehouses.find(w => w.id === item.from_warehouse_id)?.name}</TableCell>
                  <TableCell>{warehouses.find(w => w.id === item.to_warehouse_id)?.name}</TableCell>
                  <TableCell>
                    <Badge variant={item.status === 'POSTED' ? 'default' : 'secondary'}>{item.status}</Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <Button variant="ghost" size="sm" asChild>
                      <Link href={`/inventory/transfers/${item.id}`}><Eye className="h-4 w-4" /></Link>
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  );
}
