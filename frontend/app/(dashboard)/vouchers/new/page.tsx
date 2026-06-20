"use client";

import { useForm, FormProvider } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { voucherSchema, VoucherFormData } from "@/features/vouchers/schemas";
import { VoucherHeaderForm } from "@/features/vouchers/components/VoucherHeaderForm";
import { VoucherEntriesTable } from "@/features/vouchers/components/VoucherEntriesTable";
import { InventoryItemsTable } from "@/features/vouchers/components/InventoryItemsTable";
import { VoucherType } from "@/features/vouchers/types";
import { createVoucher } from "@/features/vouchers/api/vouchers-api";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";

export default function NewVoucherPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const methods = useForm<VoucherFormData>({
    resolver: zodResolver(voucherSchema),
    defaultValues: {
      voucher_type: VoucherType.JOURNAL,
      voucher_date: new Date().toISOString().split('T')[0],
      entries: [
        { ledger_id: "", debit_amount: 0, credit_amount: 0 },
        { ledger_id: "", debit_amount: 0, credit_amount: 0 },
      ],
      inventory_entries: [],
    }
  });

  const onSubmit = async (data: VoucherFormData) => {
    setLoading(true);
    setError(null);
    try {
      await createVoucher(data);
      router.push("/vouchers");
    } catch (err: any) {
      setError(err.message || "Failed to create voucher");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">New Voucher</h1>
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
              <VoucherHeaderForm />
              <VoucherEntriesTable />
              <InventoryItemsTable />

              {error && <p className="text-sm text-red-500 font-medium mb-4">{error}</p>}

              <div className="flex justify-end pt-4 border-t">
                 <Button type="submit" disabled={loading}>
                    {loading ? "Saving..." : "Save Draft Voucher"}
                 </Button>
              </div>
            </CardContent>
          </Card>
        </form>
      </FormProvider>
    </div>
  );
}
