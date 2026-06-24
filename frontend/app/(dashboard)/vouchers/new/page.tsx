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
import { Button, buttonVariants } from "@/components/ui/button";
import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Receipt, Save, ArrowLeft, CheckCircle2, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";

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
      setError(err.message || "Failed to finalize document");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-10 max-w-[1500px] mx-auto space-y-10 pb-40">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6 border-b border-slate-200 pb-10">
        <div className="flex items-center gap-6">
           <div className="bg-blue-600 p-4 rounded-[24px] shadow-2xl shadow-blue-500/40 text-white ring-8 ring-blue-50">
              <Receipt className="h-8 w-8" />
           </div>
           <div>
              <h1 className="text-4xl font-black tracking-tighter text-slate-900 uppercase italic">Voucher Entry</h1>
              <p className="text-slate-400 font-bold uppercase tracking-widest italic mt-1 italic">Drafting operational transaction protocol</p>
           </div>
        </div>
        <div className="flex gap-4">
          <Button variant="ghost" onClick={() => router.back()} className="h-14 px-8 rounded-2xl font-black uppercase tracking-widest text-slate-400 hover:text-slate-900">
            <ArrowLeft className="mr-2 h-5 w-5" /> Discard
          </Button>
          <Button
            onClick={methods.handleSubmit(onSubmit)}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 h-14 px-12 rounded-2xl shadow-2xl shadow-blue-500/40 font-black uppercase tracking-widest tracking-tight transition-all active:scale-95"
          >
            {loading ? "Establishing..." : <><Save className="mr-2 h-5 w-5" /> Save & Finalize</>}
          </Button>
        </div>
      </div>

      <FormProvider {...methods}>
        <form onSubmit={methods.handleSubmit(onSubmit)}>
           <VoucherHeaderForm />
           <VoucherEntriesTable />

           <div className="bg-slate-900 p-1 rounded-3xl overflow-hidden shadow-2xl">
              <div className="bg-slate-800 p-6 rounded-[22px] flex items-center justify-between">
                 <div className="flex items-center gap-4 text-slate-400">
                    <div className="h-2 w-2 rounded-full bg-blue-500 shadow-[0_0_10px_#2563eb]" />
                    <span className="text-[10px] font-black uppercase tracking-[0.4em]">Draft Persistence Mode</span>
                 </div>
                 <Button type="submit" disabled={loading} className="bg-white text-slate-900 hover:bg-blue-600 hover:text-white h-12 px-10 rounded-xl font-black uppercase tracking-widest shadow-xl transition-all">
                    {loading ? "Processing..." : "Commit Transaction"}
                 </Button>
              </div>
           </div>

           {error && (
              <div className="mt-8 p-5 bg-rose-600 text-white rounded-2xl flex items-center gap-4 shadow-2xl animate-in shake-1 duration-500">
                 <div className="bg-white/10 p-2 rounded-xl border border-white/20"><AlertCircle className="h-6 w-6" /></div>
                 <p className="font-black uppercase tracking-widest text-sm">{error}</p>
              </div>
           )}
        </form>
      </FormProvider>
    </div>
  );
}

