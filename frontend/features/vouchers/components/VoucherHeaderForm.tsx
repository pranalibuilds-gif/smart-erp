"use client";

import { useFormContext } from "react-hook-form";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { VoucherType } from "../types";
import { VoucherFormData } from "../schemas";

export const VoucherHeaderForm = () => {
  const { register, watch, formState: { errors } } = useFormContext<VoucherFormData>();

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-10 bg-slate-50/50 p-6 rounded-2xl border border-slate-100">
      <div className="space-y-2.5">
        <Label className="text-xs font-bold uppercase tracking-wider text-slate-500">Transaction Type</Label>
        <select
          className="w-full h-11 rounded-xl border-slate-200 bg-white px-3 text-sm font-semibold shadow-sm focus:ring-2 focus:ring-blue-500/10 outline-none"
          {...register("voucher_type")}
        >
          {Object.values(VoucherType).map(type => (
            <option key={type} value={type}>{type}</option>
          ))}
        </select>
        {errors.voucher_type && <p className="text-xs text-red-500 font-medium">{errors.voucher_type.message}</p>}
      </div>

      <div className="space-y-2.5">
        <Label className="text-xs font-bold uppercase tracking-wider text-slate-500">Voucher Date</Label>
        <Input type="date" className="h-11 rounded-xl border-slate-200 bg-white" {...register("voucher_date")} />
        {errors.voucher_date && <p className="text-xs text-red-500 font-medium">{errors.voucher_date.message}</p>}
      </div>

      <div className="space-y-2.5">
        <Label className="text-xs font-bold uppercase tracking-wider text-slate-500">Narration / Remarks</Label>
        <Input placeholder="Describe this transaction..." className="h-11 rounded-xl border-slate-200 bg-white" {...register("narration")} />
      </div>
    </div>
  );
};
