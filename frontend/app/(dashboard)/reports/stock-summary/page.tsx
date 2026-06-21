"use client";

import { useEffect, useState } from "react";
import { getStockSummary } from "@/features/reports/api/reports-api";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Card, CardContent } from "@/components/ui/card";

export default function StockSummaryPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getStockSummary()
      .then(setData)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-8">Loading...</div>;

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">Stock Summary</h1>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Item Name</TableHead>
                <TableHead className="text-right">Opening Qty</TableHead>
                <TableHead className="text-right">Inward</TableHead>
                <TableHead className="text-right">Outward</TableHead>
                <TableHead className="text-right">Closing Qty</TableHead>
                <TableHead className="text-right">Avg Cost</TableHead>
                <TableHead className="text-right">Value</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.items.map((item: any) => (
                <TableRow key={item.item_id}>
                  <TableCell className="font-medium">{item.item_name}</TableCell>
                  <TableCell className="text-right">{item.opening_qty.toFixed(3)}</TableCell>
                  <TableCell className="text-right text-green-600">+{item.inward_qty.toFixed(3)}</TableCell>
                  <TableCell className="text-right text-red-600">-{item.outward_qty.toFixed(3)}</TableCell>
                  <TableCell className="text-right font-bold">{item.closing_qty.toFixed(3)}</TableCell>
                  <TableCell className="text-right font-mono">₹{item.average_cost.toFixed(2)}</TableCell>
                  <TableCell className="text-right font-mono font-bold">₹{item.stock_value.toFixed(2)}</TableCell>
                </TableRow>
              ))}
              {data.items.length === 0 && (
                <TableRow>
                   <TableCell colSpan={7} className="text-center py-8 text-gray-400">No stock items found</TableCell>
                </TableRow>
              )}
            </TableBody>
            <TableHeader className="bg-gray-100 font-bold">
               <TableRow>
                 <TableCell colSpan={6} className="text-right">Total Inventory Value</TableCell>
                 <TableCell className="text-right font-mono text-lg text-blue-700">₹{data.total_value.toFixed(2)}</TableCell>
               </TableRow>
            </TableHeader>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
