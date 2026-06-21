"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { getTransfer, postTransfer, cancelTransfer, StockTransfer } from "@/features/inventory/api/inventory-api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useMasterStore } from "@/stores/master-store";

export default function TransferDetailPage() {
  const { id } = useParams();
  const router = useRouter();
  const [data, setData] = useState<StockTransfer | null>(null);
  const [loading, setLoading] = useState(true);
  const { stockItems, warehouses, fetchMasters } = useMasterStore();

  useEffect(() => {
    fetchMasters();
    getTransfer(id as string).then(setData).finally(() => setLoading(false));
  }, [id, fetchMasters]);

  const handlePost = async () => {
    try {
      const updated = await postTransfer(id as string);
      setData(updated);
    } catch (err: any) { alert(err.message); }
  };

  const handleCancel = async () => {
    if (!confirm("Cancel this transfer?")) return;
    try {
      const updated = await cancelTransfer(id as string);
      setData(updated);
    } catch (err: any) { alert(err.message); }
  };

  if (loading) return <div className="p-8">Loading...</div>;
  if (!data) return <div className="p-8">Not found</div>;

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <div>
           <Button variant="ghost" onClick={() => router.push("/inventory/transfers")} className="mb-2">← Back</Button>
           <h1 className="text-3xl font-bold">{data.transfer_no}</h1>
        </div>
        <div className="space-x-4">
           {data.status === 'DRAFT' && <Button onClick={handlePost}>Post Transfer</Button>}
           {data.status === 'POSTED' && <Button variant="destructive" onClick={handleCancel}>Cancel Transfer</Button>}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
         <Card><CardHeader className="py-2 text-xs text-gray-500">From</CardHeader><CardContent className="font-bold">{warehouses.find(w => w.id === data.from_warehouse_id)?.name}</CardContent></Card>
         <Card><CardHeader className="py-2 text-xs text-gray-500">To</CardHeader><CardContent className="font-bold">{warehouses.find(w => w.id === data.to_warehouse_id)?.name}</CardContent></Card>
         <Card><CardHeader className="py-2 text-xs text-gray-500">Date</CardHeader><CardContent className="font-bold">{data.transfer_date}</CardContent></Card>
         <Card><CardHeader className="py-2 text-xs text-gray-500">Status</CardHeader><CardContent><Badge>{data.status}</Badge></CardContent></Card>
      </div>

      <Card className="mb-8">
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Item</TableHead>
                <TableHead className="text-right">Quantity</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.items.map((item, i) => (
                <TableRow key={i}>
                  <TableCell>{stockItems.find(s => s.id === item.stock_item_id)?.name || item.stock_item_id}</TableCell>
                  <TableCell className="text-right font-bold">{item.quantity}</TableCell>
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
