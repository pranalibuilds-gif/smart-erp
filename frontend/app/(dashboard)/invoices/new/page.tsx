"use client";

import { useForm, FormProvider } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { invoiceSchema, InvoiceFormData } from "@/features/billing/schemas";
import { InvoiceItemsTable } from "@/features/billing/components/InvoiceItemsTable";
import { DocumentType } from "@/features/billing/types";
import { createInvoice } from "@/features/billing/api/billing-api";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { usePartyStore } from "@/stores/party-store";

export default function NewInvoicePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { parties, fetchParties } = usePartyStore();

  useEffect(() => {
    fetchParties();
  }, [fetchParties]);

  const methods = useForm<InvoiceFormData>({
    resolver: zodResolver(invoiceSchema),
    defaultValues: {
      document_type: DocumentType.SALES,
      invoice_date: new Date().toISOString().split('T')[0],
      items: [{ item_name: "", quantity: 1, rate: 0, tax_rate: 18 }],
    }
  });

  const onSubmit = async (data: InvoiceFormData) => {
    setLoading(true);
    setError(null);
    try {
      await createInvoice(data);
      router.push("/invoices");
    } catch (err: any) {
      setError(err.message || "Failed to create invoice");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">New Document</h1>
        <div className="space-x-4">
          <Button variant="outline" onClick={() => router.back()}>Discard</Button>
          <Button onClick={methods.handleSubmit(onSubmit)} disabled={loading}>
            {loading ? "Saving..." : "Save Draft"}
          </Button>
        </div>
      </div>

      <FormProvider {...methods}>
        <form onSubmit={methods.handleSubmit(onSubmit)}>
          <Card>
            <CardContent className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="space-y-2">
                  <Label>Document Type</Label>
                  <Select
                    value={methods.watch("document_type")}
                    onValueChange={(val) => methods.setValue("document_type", val as DocumentType)}
                  >
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value={DocumentType.SALES}>Sales Invoice</SelectItem>
                      <SelectItem value={DocumentType.PURCHASE}>Purchase Invoice</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Party (Customer/Supplier)</Label>
                  <select
                    className="w-full h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                    {...methods.register("party_id")}
                  >
                    <option value="">Select Party</option>
                    {parties.map(p => (
                      <option key={p.id} value={p.id}>{p.name}</option>
                    ))}
                  </select>
                  {methods.formState.errors.party_id && <p className="text-xs text-red-500">{methods.formState.errors.party_id.message}</p>}
                </div>

                <div className="space-y-2">
                  <Label>Date</Label>
                  <Input type="date" {...methods.register("invoice_date")} />
                </div>
              </div>

              <InvoiceItemsTable />

              <div className="space-y-2 mb-8">
                <Label>Narration</Label>
                <Input placeholder="General notes..." {...methods.register("narration")} />
              </div>

              {error && <p className="text-sm text-red-500 font-medium mb-4">{error}</p>}

              <div className="flex justify-end pt-4 border-t">
                 <Button type="submit" disabled={loading}>Save Document</Button>
              </div>
            </CardContent>
          </Card>
        </form>
      </FormProvider>
    </div>
  );
}
