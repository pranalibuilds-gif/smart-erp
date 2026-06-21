"use client";

import { useForm, FormProvider, useFieldArray } from "react-hook-form";
import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import { useMasterStore } from "@/stores/master-store";
import { createPayment } from "@/features/banking/api/banking-api";
import { Card, CardContent } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Trash2, Plus } from "lucide-react";
import apiClient from "@/lib/api-client";

export default function NewPaymentPage() {
  const router = useRouter();
  const { ledgers, fetchMasters } = useMasterStore();
  const [loading, setLoading] = useState(false);
  const [invoices, setInvoices] = useState<any[]>([]);

  useEffect(() => {
    fetchMasters();
    // Load unpaid purchase invoices for the company (simple load all for now)
    apiClient.get("/api/v1/billing/invoices").then(res => {
       setInvoices(res.data.data.filter((i: any) => i.document_type === 'PURCHASE' && i.status === 'POSTED'));
    });
  }, [fetchMasters]);

  const methods = useForm({
    defaultValues: {
      voucher_date: new Date().toISOString().split('T')[0],
      party_ledger_id: "",
      bank_cash_ledger_id: "",
      amount: 0,
      narration: "",
      allocations: [] as any[]
    }
  });

  const { fields, append, remove } = useFieldArray({ control: methods.control, name: "allocations" });

  const onSubmit = async (data: any) => {
    setLoading(true);
    try {
      await createPayment(data);
      router.push("/banking");
    } catch (err: any) {
      alert(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">New Payment Voucher</h1>

      <FormProvider {...methods}>
        <form onSubmit={methods.handleSubmit(onSubmit)}>
          <Card>
            <CardContent className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                <div className="space-y-2">
                  <Label>Bank / Cash Account</Label>
                  <select className="w-full h-9 rounded-md border border-input px-3 text-sm" {...methods.register("bank_cash_ledger_id")}>
                    <option value="">Select Account</option>
                    {ledgers.map(l => <option key={l.id} value={l.id}>{l.name}</option>)}
                  </select>
                </div>
                <div className="space-y-2">
                  <Label>Date</Label>
                  <Input type="date" {...methods.register("voucher_date")} />
                </div>
                <div className="space-y-2">
                  <Label>Pay To (Party Ledger)</Label>
                  <select className="w-full h-9 rounded-md border border-input px-3 text-sm" {...methods.register("party_ledger_id")}>
                    <option value="">Select Party</option>
                    {ledgers.map(l => <option key={l.id} value={l.id}>{l.name}</option>)}
                  </select>
                </div>
                <div className="space-y-2">
                  <Label>Amount</Label>
                  <Input type="number" step="0.01" {...methods.register("amount")} />
                </div>
              </div>

              <div className="mb-8">
                <h2 className="text-lg font-semibold mb-4">Invoice Allocations</h2>
                <div className="border rounded-md">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="w-[60%]">Invoice</TableHead>
                        <TableHead className="text-right">Amount Allocated</TableHead>
                        <TableHead className="w-[50px]"></TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {fields.map((field, index) => (
                        <TableRow key={field.id}>
                          <TableCell>
                            <select className="w-full h-9 rounded-md border border-input px-3 text-sm" {...methods.register(`allocations.${index}.invoice_id` as const)}>
                              <option value="">Select Invoice</option>
                              {invoices.map(i => <option key={i.id} value={i.id}>{i.invoice_number} (₹{i.total_amount})</option>)}
                            </select>
                          </TableCell>
                          <TableCell>
                            <Input type="number" step="0.01" className="text-right" {...methods.register(`allocations.${index}.allocated_amount` as const)} />
                          </TableCell>
                          <TableCell>
                            <Button variant="ghost" size="icon" onClick={() => remove(index)}><Trash2 className="h-4 w-4 text-red-500" /></Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
                <Button type="button" variant="outline" size="sm" className="mt-4" onClick={() => append({ invoice_id: "", allocated_amount: 0 })}>
                  <Plus className="mr-2 h-4 w-4" /> Add Invoice
                </Button>
              </div>

              <div className="space-y-2 mb-8">
                <Label>Narration</Label>
                <Input placeholder="Payment details..." {...methods.register("narration")} />
              </div>

              <div className="flex justify-end gap-4 border-t pt-4">
                <Button variant="outline" type="button" onClick={() => router.back()}>Cancel</Button>
                <Button type="submit" disabled={loading}>Post Payment</Button>
              </div>
            </CardContent>
          </Card>
        </form>
      </FormProvider>
    </div>
  );
}
