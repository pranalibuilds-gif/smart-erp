"use client";

import { useEffect, useState } from "react";
import { listAdjustments, StockAdjustment } from "@/features/inventory/api/inventory-api";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Plus, Eye } from "lucide-react";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export default function StockAdjustmentsPage() {
  const [items, setItems] = useState<StockAdjustment[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listAdjustments().then(setItems).finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold">Stock Adjustments</h1>
        <Link href="/inventory/adjustments/new" className={cn(buttonVariants(), "bg-blue-600 hover:bg-blue-700")}>
          <Plus className="mr-2 h-4 w-4" /> New Adjustment
        </Link>
      </div>

      {loading ? <div>Loading...</div> : (
        <div className="bg-white border rounded-lg overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Number</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Reason</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {items.map((item) => (
                <TableRow key={item.id}>
                  <TableCell className="font-medium">{item.adjustment_no}</TableCell>
                  <TableCell>{item.adjustment_date}</TableCell>
                  <TableCell>{item.reason}</TableCell>
                  <TableCell>
                    <Badge variant={item.status === 'POSTED' ? 'default' : 'secondary'}>{item.status}</Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <Link href={`/inventory/adjustments/${item.id}`} className={cn(buttonVariants({ variant: "ghost", size: "sm" }))}>
                      <Eye className="h-4 w-4" />
                    </Link>
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
