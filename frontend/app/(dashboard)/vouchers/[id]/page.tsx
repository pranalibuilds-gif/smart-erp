"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { getVoucher, postVoucher, cancelVoucher } from "@/features/vouchers/api/vouchers-api";
import { Voucher, VoucherStatus } from "@/features/vouchers/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useMasterStore } from "@/stores/master-store";

export default function VoucherDetailPage() {
  const { id } = useParams();
  const router = useRouter();
  const [voucher, setVoucher] = useState<Voucher | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const { ledgers, stockItems, fetchMasters } = useMasterStore();

  useEffect(() => {
    fetchMasters();
    getVoucher(id as string)
      .then(setVoucher)
      .finally(() => setLoading(false));
  }, [id, fetchMasters]);

  const handlePost = async () => {
    if (!voucher) return;
    setActionLoading(true);
    try {
      const updated = await postVoucher(voucher.id);
      setVoucher(updated);
    } catch (err: any) {
      alert(err.message);
    } finally {
      setActionLoading(false);
    }
  };

  const handleCancel = async () => {
    if (!voucher) return;
    if (!confirm("Are you sure you want to cancel this voucher?")) return;
    setActionLoading(true);
    try {
      const updated = await cancelVoucher(voucher.id);
      setVoucher(updated);
    } catch (err: any) {
      alert(err.message);
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) return <div className="p-8">Loading...</div>;
  if (!voucher) return <div className="p-8 text-red-500">Voucher not found</div>;

  const totalDebit = voucher.entries.reduce((sum, e) => sum + Number(e.debit_amount), 0);

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <div>
           <Button variant="ghost" onClick={() => router.push("/vouchers")} className="mb-2">← Back to List</Button>
           <h1 className="text-3xl font-bold">{voucher.voucher_number}</h1>
        </div>
        <div className="space-x-4">
           {voucher.status === VoucherStatus.DRAFT && (
             <Button onClick={handlePost} disabled={actionLoading}>
                {actionLoading ? "Posting..." : "Post Voucher"}
             </Button>
           )}
           {voucher.status === VoucherStatus.POSTED && (
             <Button variant="destructive" onClick={handleCancel} disabled={actionLoading}>
                {actionLoading ? "Cancelling..." : "Cancel Voucher"}
             </Button>
           )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card>
          <CardHeader className="py-4"><CardTitle className="text-sm font-medium text-gray-500">Details</CardTitle></CardHeader>
          <CardContent>
            <div className="text-lg font-bold uppercase">{voucher.voucher_type}</div>
            <div className="text-sm text-gray-600">Date: {voucher.voucher_date}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="py-4"><CardTitle className="text-sm font-medium text-gray-500">Status</CardTitle></CardHeader>
          <CardContent>
            <Badge variant="secondary" className="text-lg uppercase px-3 py-1">{voucher.status}</Badge>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="py-4"><CardTitle className="text-sm font-medium text-gray-500">Total Amount</CardTitle></CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-mono">₹{totalDebit.toFixed(2)}</div>
          </CardContent>
        </Card>
      </div>

      <Card className="mb-8">
        <CardHeader><CardTitle className="text-lg">Accounting Entries</CardTitle></CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Ledger</TableHead>
                <TableHead className="text-right">Debit</TableHead>
                <TableHead className="text-right">Credit</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {voucher.entries.map((e, i) => (
                <TableRow key={i}>
                  <TableCell>{ledgers.find(l => l.id === e.ledger_id)?.name || e.ledger_id}</TableCell>
                  <TableCell className="text-right">{Number(e.debit_amount) > 0 ? Number(e.debit_amount).toFixed(2) : "-"}</TableCell>
                  <TableCell className="text-right">{Number(e.credit_amount) > 0 ? Number(e.credit_amount).toFixed(2) : "-"}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {voucher.inventory_entries.length > 0 && (
        <Card className="mb-8 border-dashed border-2">
          <CardHeader><CardTitle className="text-lg">Inventory Transactions</CardTitle></CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Item</TableHead>
                  <TableHead className="text-right">Quantity</TableHead>
                  <TableHead className="text-right">Rate</TableHead>
                  <TableHead className="text-right">Amount</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {voucher.inventory_entries.map((e, i) => (
                  <TableRow key={i}>
                    <TableCell>{stockItems.find(item => item.id === e.stock_item_id)?.name || e.stock_item_id}</TableCell>
                    <TableCell className="text-right">{Number(e.quantity).toFixed(3)}</TableCell>
                    <TableCell className="text-right">{Number(e.rate).toFixed(2)}</TableCell>
                    <TableCell className="text-right font-bold">{Number(e.amount).toFixed(2)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}

      {voucher.narration && (
        <Card>
           <CardHeader><CardTitle className="text-sm font-medium text-gray-500">Narration</CardTitle></CardHeader>
           <CardContent><p className="text-gray-700 italic">"{voucher.narration}"</p></CardContent>
        </Card>
      )}
    </div>
  );
}
