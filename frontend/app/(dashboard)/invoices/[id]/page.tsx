"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { getInvoice, postInvoice, cancelInvoice } from "@/features/billing/api/billing-api";
import { Invoice, InvoiceStatus } from "@/features/billing/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { usePartyStore } from "@/stores/party-store";

export default function InvoiceDetailPage() {
  const { id } = useParams();
  const router = useRouter();
  const [invoice, setInvoice] = useState<Invoice | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const { parties, fetchParties } = usePartyStore();

  useEffect(() => {
    fetchParties();
    getInvoice(id as string)
      .then(setInvoice)
      .finally(() => setLoading(false));
  }, [id, fetchParties]);

  const handlePost = async () => {
    if (!invoice) return;
    setActionLoading(true);
    try {
      const updated = await postInvoice(invoice.id);
      setInvoice(updated);
    } catch (err: any) {
      alert(err.message);
    } finally {
      setActionLoading(false);
    }
  };

  const handleCancel = async () => {
    if (!invoice) return;
    if (!confirm("Cancel this document? Linked vouchers will also be cancelled.")) return;
    setActionLoading(true);
    try {
      const updated = await cancelInvoice(invoice.id);
      setInvoice(updated);
    } catch (err: any) {
      alert(err.message);
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) return <div className="p-8">Loading...</div>;
  if (!invoice) return <div className="p-8 text-red-500">Document not found</div>;

  const partyName = parties.find(p => p.id === invoice.party_id)?.name || invoice.party_id;

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <div>
           <Button variant="ghost" onClick={() => router.push("/invoices")} className="mb-2">← Back to List</Button>
           <h1 className="text-3xl font-bold">{invoice.invoice_number}</h1>
        </div>
        <div className="space-x-4">
           {invoice.status === InvoiceStatus.DRAFT && (
             <Button onClick={handlePost} disabled={actionLoading}>Post & Generate Voucher</Button>
           )}
           {invoice.status === InvoiceStatus.POSTED && (
             <Button variant="destructive" onClick={handleCancel} disabled={actionLoading}>Cancel Document</Button>
           )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card>
          <CardHeader className="py-4"><CardTitle className="text-sm font-medium text-gray-500">Party</CardTitle></CardHeader>
          <CardContent><div className="text-lg font-bold">{partyName}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="py-4"><CardTitle className="text-sm font-medium text-gray-500">Document Type</CardTitle></CardHeader>
          <CardContent><Badge className="uppercase">{invoice.document_type}</Badge></CardContent>
        </Card>
        <Card>
          <CardHeader className="py-4"><CardTitle className="text-sm font-medium text-gray-500">Invoice Date</CardTitle></CardHeader>
          <CardContent><div className="text-lg font-mono">{invoice.invoice_date}</div></CardContent>
        </Card>
      </div>

      <Card className="mb-8">
        <CardHeader><CardTitle className="text-lg">Items</CardTitle></CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Item Name</TableHead>
                <TableHead className="text-right">Quantity</TableHead>
                <TableHead className="text-right">Rate</TableHead>
                <TableHead className="text-right">Tax %</TableHead>
                <TableHead className="text-right">Amount</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {invoice.items.map((item, i) => (
                <TableRow key={i}>
                  <TableCell>
                    <div className="font-medium">{item.item_name}</div>
                    {item.item_code && <div className="text-xs text-gray-500">{item.item_code}</div>}
                  </TableCell>
                  <td className="text-right">{item.quantity}</td>
                  <td className="text-right">{item.rate}</td>
                  <td className="text-right">{item.tax_rate}%</td>
                  <td className="text-right font-bold">₹{item.total_amount.toFixed(2)}</td>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          <div className="mt-8 flex justify-end">
             <div className="w-64 space-y-2 border-t pt-4">
                <div className="flex justify-between text-sm">
                   <span className="text-gray-500">Taxable:</span>
                   <span>₹{Number(invoice.taxable_amount).toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-sm">
                   <span className="text-gray-500">Tax Total:</span>
                   <span>₹{Number(invoice.tax_amount).toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-xl font-bold text-blue-600">
                   <span>Grand Total:</span>
                   <span>₹{Number(invoice.total_amount).toFixed(2)}</span>
                </div>
             </div>
          </div>
        </CardContent>
      </Card>

      {invoice.voucher_id && (
        <Card className="mb-8 border-blue-200 bg-blue-50">
           <CardContent className="p-4 flex justify-between items-center">
              <span className="text-sm text-blue-700">Linked to accounting voucher</span>
              <Button variant="link" onClick={() => router.push(`/vouchers/${invoice.voucher_id}`)}>View Voucher →</Button>
           </CardContent>
        </Card>
      )}

      {invoice.narration && (
        <Card>
           <CardContent className="p-4 text-gray-600 italic">"{invoice.narration}"</CardContent>
        </Card>
      )}
    </div>
  );
}
