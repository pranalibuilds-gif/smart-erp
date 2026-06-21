"use client";

import { useEffect, useState } from "react";
import apiClient from "@/lib/api-client";
import { useMasterStore } from "@/stores/master-store";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";

export default function StockByWarehousePage() {
  const { warehouses, fetchMasters } = useMasterStore();
  const [selectedWh, setSelectedWh] = useState("");
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchMasters();
  }, [fetchMasters]);

  useEffect(() => {
    if (selectedWh) {
      setLoading(true);
      apiClient.get(`/api/v1/reports/warehouse-stock/${selectedWh}`)
        .then(res => setData(res.data.data))
        .finally(() => setLoading(false));
    } else {
      setData(null);
    }
  }, [selectedWh]);

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">Stock By Warehouse</h1>

      <div className="max-w-xs mb-8">
        <Label>Select Warehouse</Label>
        <select
          className="w-full h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm mt-2"
          value={selectedWh}
          onChange={(e) => setSelectedWh(e.target.value)}
        >
          <option value="">Choose...</option>
          {warehouses.map(w => <option key={w.id} value={w.id}>{w.name}</option>)}
        </select>
      </div>

      {loading ? <div>Loading...</div> : data && (
        <Card>
          <CardHeader><CardTitle>{data.warehouse_name}</CardTitle></CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Item Name</TableHead>
                  <TableHead className="text-right">Quantity</TableHead>
                  <TableHead className="text-right">Avg Cost</TableHead>
                  <TableHead className="text-right">Value</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.items.map((item: any) => (
                  <TableRow key={item.item_id}>
                    <TableCell className="font-medium">{item.item_name}</TableCell>
                    <TableCell className="text-right">{item.quantity.toFixed(3)}</TableCell>
                    <TableCell className="text-right font-mono">₹{item.average_cost.toFixed(2)}</TableCell>
                    <TableCell className="text-right font-mono font-bold">₹{item.value.toFixed(2)}</TableCell>
                  </TableRow>
                ))}
                {data.items.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={4} className="text-center py-8 text-gray-400">No stock found in this warehouse</TableCell>
                  </TableRow>
                )}
              </TableBody>
              <TableHeader className="bg-gray-50 font-bold">
                 <TableRow>
                   <TableCell colSpan={3} className="text-right">Warehouse Total Value</TableCell>
                   <TableCell className="text-right font-mono text-lg text-blue-700">₹{data.total_value.toFixed(2)}</TableCell>
                 </TableRow>
              </TableHeader>
            </Table>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
