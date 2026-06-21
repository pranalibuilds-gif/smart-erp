"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { getAdjustment, postAdjustment, cancelAdjustment, StockAdjustment } from "@/features/inventory/api/inventory-api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useMasterStore } from "@/stores/master-store";

export default function AdjustmentDetailPage() {
  const { id } = useParams();
  const router = useRouter();
  const [data, setData] = useState<StockAdjustment | null>(null);
  const [loading, setLoading] = useState(true);
  const { stockItems, warehouses, fetchMasters } = useMasterStore();

  useEffect(() => {
    fetchMasters();
    getAdjustment(id as string).then(setData).finally(() => setLoading(false));
  }, [id, fetchMasters]);

  const handlePost = async () => {
    try {
      const updated = await postAdjustment(id as string);
      setData(updated);
    } catch (err: any) { alert(err.message); }
  };

  const handleCancel = async () => {
    if (!confirm("Cancel this adjustment?")) return;
    try {
      const updated = await cancelAdjustment(id as string);
      setData(updated);
    } catch (err: any) { alert(err.message); }
  };

  if (loading) return <div className="p-8">Loading...</div>;
  if (!data) return <div className="p-8">Not found</div>;

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <div>
           <Button variant="ghost" onClick={() => router.push("/inventory/adjustments")} className="mb-2">← Back</Button>
           <h1 className="text-3xl font-bold">{data.adjustment_no}</h1>
        </div>
        <div className="space-x-4">
           {data.status === 'DRAFT' && <Button onClick={handlePost}>Post Adjustment</Button>}
           {data.status === 'POSTED' && <Button variant="destructive" onClick={handleCancel}>Cancel Adjustment</Button>}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
         <Card><CardHeader className="py-2 text-xs text-gray-500">Warehouse</CardHeader><CardContent className="font-bold">{warehouses.find(w => w.id === data.warehouse_id)?.name}</CardContent></Card>
         <Card><CardHeader className="py-2 text-xs text-gray-500">Date</CardHeader><CardContent className="font-bold">{data.adjustment_date}</CardContent></Card>
         <Card><CardHeader className="py-2 text-xs text-gray-500">Status</CardHeader><CardContent><Badge>{data.status}</Badge></CardContent></Card>
      </div>

      <Card className="mb-8">
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Item</TableHead>
                <TableHead className="text-right">System Qty</TableHead>
                <TableHead className="text-right">Physical Qty</TableHead>
                <TableHead className="text-right">Difference</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.items.map((item, i) => (
                <TableRow key={i}>
                  <TableCell>{stockItems.find(s => s.id === item.stock_item_id)?.name || item.stock_item_id}</TableCell>
                  <TableCell className="text-right">{item.system_quantity}</TableCell>
                  <TableCell className="text-right">{item.physical_quantity}</TableCell>
                  <TableCell className={`text-right font-bold ${item.difference_quantity >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {item.difference_quantity > 0 ? '+' : ''}{item.difference_quantity}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {data.voucher_id && (
         <Button variant="link" onClick={() => router.push(`/vouchers/${data.voucher_id}`)}>View Linked Voucher →</Button>
      )}
    </div>
  );
}
