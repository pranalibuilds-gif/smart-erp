"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { getVoucher, postVoucher, cancelVoucher } from "@/features/vouchers/api/vouchers-api";
import { Voucher, VoucherStatus } from "@/features/vouchers/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useMasterStore } from "@/stores/master-store";
import {
  ArrowLeft,
  Printer,
  CheckCircle2,
  XCircle,
  Clock,
  Receipt,
  FileText,
  CreditCard,
  Package
} from "lucide-react";
import { cn } from "@/lib/utils";

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

  if (loading) return <div className="p-8 flex justify-center items-center h-96 text-slate-400">Loading Voucher Details...</div>;
  if (!voucher) return <div className="p-8 text-center text-red-500">Voucher not found</div>;

  const totalDebit = voucher.entries.reduce((sum, e) => sum + Number(e.debit_amount), 0);
  const totalCredit = voucher.entries.reduce((sum, e) => sum + Number(e.credit_amount), 0);

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8 pb-20">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div className="space-y-4">
          <Button variant="ghost" onClick={() => router.push("/vouchers")} className="text-slate-500 hover:text-slate-900 -ml-2">
            <ArrowLeft className="mr-2 h-4 w-4" /> Back to Journal
          </Button>
          <div className="flex items-center gap-4">
             <div className="bg-blue-600 p-3 rounded-2xl shadow-lg shadow-blue-600/20">
                <Receipt className="h-6 w-6 text-white" />
             </div>
             <div>
                <h1 className="text-3xl font-bold tracking-tight text-slate-900">{voucher.voucher_number}</h1>
                <p className="text-slate-500 font-medium">Recorded on {voucher.voucher_date}</p>
             </div>
          </div>
        </div>

        <div className="flex gap-3">
           <Button variant="outline" className="bg-white">
              <Printer className="mr-2 h-4 w-4" /> Print
           </Button>
           {voucher.status === VoucherStatus.DRAFT && (
             <Button onClick={handlePost} disabled={actionLoading} className="bg-emerald-600 hover:bg-emerald-700 shadow-lg shadow-emerald-200">
                {actionLoading ? "Processing..." : <><CheckCircle2 className="mr-2 h-4 w-4" /> Post to Ledger</>}
             </Button>
           )}
           {voucher.status === VoucherStatus.POSTED && (
             <Button variant="destructive" onClick={handleCancel} disabled={actionLoading} className="shadow-lg shadow-rose-200">
                {actionLoading ? "Processing..." : <><XCircle className="mr-2 h-4 w-4" /> Cancel Voucher</>}
             </Button>
           )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <Card className="border-none shadow-sm ring-1 ring-slate-200">
          <CardHeader className="pb-2"><CardDescription className="font-bold uppercase text-[10px] tracking-widest text-slate-500">Classification</CardDescription></CardHeader>
          <CardContent>
            <p className="text-xl font-bold text-slate-900">{voucher.voucher_type}</p>
          </CardContent>
        </Card>

        <Card className="border-none shadow-sm ring-1 ring-slate-200">
          <CardHeader className="pb-2"><CardDescription className="font-bold uppercase text-[10px] tracking-widest text-slate-500">Status</CardDescription></CardHeader>
          <CardContent>
             <Badge className={cn(
               "text-sm font-bold",
               voucher.status === VoucherStatus.POSTED && "bg-emerald-50 text-emerald-700 border-emerald-100",
               voucher.status === VoucherStatus.CANCELLED && "bg-rose-50 text-rose-700 border-rose-100",
               voucher.status === VoucherStatus.DRAFT && "bg-amber-50 text-amber-700 border-amber-100"
             )} variant="outline">
                {voucher.status === VoucherStatus.POSTED && <CheckCircle2 className="mr-1.5 h-3 w-3" />}
                {voucher.status === VoucherStatus.CANCELLED && <XCircle className="mr-1.5 h-3 w-3" />}
                {voucher.status === VoucherStatus.DRAFT && <Clock className="mr-1.5 h-3 w-3" />}
                {voucher.status}
             </Badge>
          </CardContent>
        </Card>

        <Card className="lg:col-span-2 border-none shadow-sm ring-1 ring-blue-600 bg-blue-600 text-white">
          <CardHeader className="pb-2"><CardDescription className="font-bold uppercase text-[10px] tracking-widest text-blue-200">Total Transaction Value</CardDescription></CardHeader>
          <CardContent className="flex items-center justify-between">
            <h3 className="text-3xl font-bold">₹{totalDebit.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</h3>
            <CreditCard className="h-8 w-8 opacity-20" />
          </CardContent>
        </Card>
      </div>

      <Card className="border-none shadow-sm ring-1 ring-slate-200 overflow-hidden">
        <CardHeader className="bg-slate-50/50 border-b">
          <CardTitle className="text-lg flex items-center gap-2">
            <FileText className="h-5 w-5 text-blue-600" />
            Accounting Entries
          </CardTitle>
          <CardDescription>Double-entry validation for this transaction</CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader className="bg-white border-b">
              <TableRow className="hover:bg-transparent">
                <TableHead className="font-bold text-slate-900 py-4">Account Ledger</TableHead>
                <TableHead className="text-right font-bold text-slate-900">Debit (Dr)</TableHead>
                <TableHead className="text-right font-bold text-slate-900">Credit (Cr)</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {voucher.entries.map((e, i) => (
                <TableRow key={i} className="hover:bg-slate-50/50 transition-colors">
                  <TableCell className="font-medium py-4">
                     {ledgers.find(l => l.id === e.ledger_id)?.name || e.ledger_id}
                  </TableCell>
                  <TableCell className="text-right font-mono text-slate-700">
                    {Number(e.debit_amount) > 0 ? `₹${Number(e.debit_amount).toLocaleString()}` : "—"}
                  </TableCell>
                  <TableCell className="text-right font-mono text-slate-700">
                    {Number(e.credit_amount) > 0 ? `₹${Number(e.credit_amount).toLocaleString()}` : "—"}
                  </TableCell>
                </TableRow>
              ))}
              <TableRow className="bg-slate-50/50 font-bold hover:bg-slate-50/50">
                <TableCell className="text-slate-900 py-4">Voucher Total</TableCell>
                <TableCell className="text-right font-mono text-blue-700">₹{totalDebit.toLocaleString()}</TableCell>
                <TableCell className="text-right font-mono text-blue-700">₹{totalCredit.toLocaleString()}</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {voucher.inventory_entries.length > 0 && (
        <Card className="border-none shadow-sm ring-1 ring-slate-200 overflow-hidden border-t-4 border-t-orange-500">
          <CardHeader className="bg-slate-50/50 border-b">
            <CardTitle className="text-lg flex items-center gap-2">
              <Package className="h-5 w-5 text-orange-500" />
              Inventory Transactions
            </CardTitle>
            <CardDescription>Stock movements linked to this voucher</CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader className="bg-white border-b">
                <TableRow className="hover:bg-transparent">
                  <TableHead className="font-bold text-slate-900 py-4">Stock Item</TableHead>
                  <TableHead className="text-right font-bold text-slate-900">Quantity</TableHead>
                  <TableHead className="text-right font-bold text-slate-900">Rate</TableHead>
                  <TableHead className="text-right font-bold text-slate-900">Amount</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {voucher.inventory_entries.map((e, i) => (
                  <TableRow key={i} className="hover:bg-slate-50/50 transition-colors">
                    <TableCell className="font-medium py-4">
                       {stockItems.find(item => item.id === e.stock_item_id)?.name || e.stock_item_id}
                    </TableCell>
                    <TableCell className="text-right font-mono font-bold text-slate-700">
                       {Number(e.quantity).toFixed(3)}
                    </TableCell>
                    <TableCell className="text-right font-mono text-slate-500">
                       ₹{Number(e.rate).toLocaleString()}
                    </TableCell>
                    <TableCell className="text-right font-mono font-bold text-orange-600">
                       ₹{Number(e.amount).toLocaleString()}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}

      {voucher.narration && (
        <div className="bg-slate-50 p-6 rounded-xl border border-slate-200 border-dashed">
           <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">Narration / Internal Notes</h4>
           <p className="text-slate-600 italic leading-relaxed">"{voucher.narration}"</p>
        </div>
      )}
    </div>
  );
}
