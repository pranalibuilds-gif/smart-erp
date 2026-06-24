"use client";

import { useFieldArray, useFormContext } from "react-hook-form";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Trash2, Plus, ArrowRightLeft, Info, HelpCircle } from "lucide-react";
import { VoucherFormData } from "../schemas";
import { useMasterStore } from "@/stores/master-store";
import { useEffect } from "react";
import { cn } from "@/lib/utils";

export const VoucherEntriesTable = () => {
  const { control, register, watch, formState: { errors } } = useFormContext<VoucherFormData>();
  const { fields, append, remove } = useFieldArray({ control, name: "entries" });
  const { ledgers, fetchMasters } = useMasterStore();

  useEffect(() => {
    fetchMasters();
  }, [fetchMasters]);

  const entries = watch("entries");
  const totalDebit = entries?.reduce((sum, e) => sum + (Number(e.debit_amount) || 0), 0) || 0;
  const totalCredit = entries?.reduce((sum, e) => sum + (Number(e.credit_amount) || 0), 0) || 0;
  const difference = Math.abs(totalDebit - totalCredit);
  const isBalanced = difference < 0.01 && (totalDebit > 0 || totalCredit > 0);

  return (
    <div className="space-y-8 mb-12 animate-in fade-in duration-500">
      <div className="flex items-center justify-between border-b border-slate-100 pb-6 px-2">
         <div className="flex items-center gap-4">
            <div className="bg-blue-600/10 p-3 rounded-2xl border border-blue-200">
               <ArrowRightLeft className="h-5 w-5 text-blue-600" />
            </div>
            <div>
               <h2 className="text-xl font-black tracking-tight text-slate-900 uppercase italic">Double Entry Journal</h2>
               <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mt-0.5">Validation state: {isBalanced ? 'Balanced' : 'Unbalanced'}</p>
            </div>
         </div>
         <Button
            type="button"
            variant="outline"
            size="sm"
            className="rounded-xl border-blue-200 bg-white text-blue-600 hover:bg-blue-600 hover:text-white h-11 px-6 font-black uppercase tracking-widest shadow-sm transition-all"
            onClick={() => append({ ledger_id: "", debit_amount: 0, credit_amount: 0 })}
          >
            <Plus className="mr-2 h-4 w-4" /> New Row Entry
          </Button>
      </div>

      <div className="bg-white border border-slate-200 rounded-[24px] shadow-sm overflow-hidden ring-1 ring-slate-200/60">
        <Table>
          <TableHeader className="bg-slate-50/50">
            <TableRow className="hover:bg-transparent">
              <TableHead className="font-black text-slate-500 uppercase tracking-[0.15em] py-6 px-10 text-[10px] w-1/2">Account / Ledger Context</TableHead>
              <TableHead className="font-black text-slate-500 uppercase tracking-[0.15em] text-[10px] text-right w-44">Debit (₹)</TableHead>
              <TableHead className="font-black text-slate-500 uppercase tracking-[0.15em] text-[10px] text-right w-44">Credit (₹)</TableHead>
              <TableHead className="w-20"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {fields.map((field, index) => (
              <TableRow key={field.id} className="hover:bg-blue-50/20 transition-all border-b last:border-0 border-slate-100 group h-20">
                <TableCell className="px-10">
                  <div className="relative">
                    <select
                      className="w-full h-12 rounded-2xl border border-slate-200 bg-white px-5 text-sm font-black text-slate-800 focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 outline-none transition-all appearance-none cursor-pointer"
                      {...register(`entries.${index}.ledger_id` as const)}
                    >
                      <option value="">Select Target Ledger Account...</option>
                      {ledgers.map(l => (
                        <option key={l.id} value={l.id}>{l.name.toUpperCase()}</option>
                      ))}
                    </select>
                    <div className="absolute right-5 top-1/2 -translate-y-1/2 pointer-events-none opacity-20 group-focus-within:opacity-100 transition-opacity">
                       <HelpCircle className="h-4 w-4 text-blue-600" />
                    </div>
                  </div>
                </TableCell>
                <TableCell>
                  <div className="relative group/input">
                    <Input
                      type="number"
                      step="0.01"
                      className="text-right h-12 font-mono font-black text-lg text-slate-900 rounded-2xl border-slate-200 bg-white px-6 focus:bg-white shadow-none transition-all"
                      placeholder="0.00"
                      {...register(`entries.${index}.debit_amount` as const)}
                    />
                    <div className="absolute left-3 top-1/2 -translate-y-1/2 opacity-10 font-black text-[10px] uppercase">DR</div>
                  </div>
                </TableCell>
                <TableCell>
                  <div className="relative group/input">
                    <Input
                      type="number"
                      step="0.01"
                      className="text-right h-12 font-mono font-black text-lg text-slate-900 rounded-2xl border-slate-200 bg-white px-6 focus:bg-white shadow-none transition-all"
                      placeholder="0.00"
                      {...register(`entries.${index}.credit_amount` as const)}
                    />
                    <div className="absolute left-3 top-1/2 -translate-y-1/2 opacity-10 font-black text-[10px] uppercase">CR</div>
                  </div>
                </TableCell>
                <TableCell className="text-right pr-6">
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-10 w-10 rounded-xl text-slate-300 hover:text-rose-600 hover:bg-rose-50 transition-all opacity-0 group-hover:opacity-100 group-hover:translate-x-0 translate-x-2 duration-300"
                    onClick={() => remove(index)}
                  >
                    <Trash2 className="h-5 w-5" />
                  </Button>
                </TableCell>
              </TableRow>
            ))}

            <TableRow className="bg-slate-900 text-white font-black border-t-4 border-blue-600 shadow-2xl relative z-10">
              <TableCell className="text-right px-10 py-10 uppercase tracking-[0.2em] text-[11px] italic text-blue-400">Ledger Aggregation Check</TableCell>
              <TableCell className="text-right font-mono text-2xl py-10 tracking-tighter">₹{totalDebit.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</TableCell>
              <TableCell className="text-right font-mono text-2xl py-10 tracking-tighter">₹{totalCredit.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</TableCell>
              <TableCell className="px-6 py-10">
                 {isBalanced && (
                   <div className="bg-emerald-500/20 p-2 rounded-xl border border-emerald-500/20">
                      <div className="h-2 w-2 rounded-full bg-emerald-400 shadow-[0_0_10px_#34d399]" />
                   </div>
                 )}
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </div>

      {!isBalanced && (totalDebit > 0 || totalCredit > 0) && (
         <div className="p-6 bg-rose-50 border border-rose-200 rounded-[20px] flex items-center justify-between text-rose-700 animate-in zoom-in-95 duration-300 shadow-lg shadow-rose-900/5">
            <div className="flex items-center gap-4">
               <div className="bg-rose-600 h-10 w-10 rounded-xl flex items-center justify-center text-white shadow-lg shadow-rose-600/30">
                  <Info className="h-6 w-6" />
               </div>
               <div>
                  <p className="text-sm font-black uppercase tracking-wider">Accounting Mismatch</p>
                  <p className="text-xs font-bold opacity-70 mt-0.5">Voucher cannot be posted until debit equals credit. Adjust entries to proceed.</p>
               </div>
            </div>
            <div className="text-right">
               <p className="text-[10px] font-black uppercase tracking-widest opacity-50 mb-1">Difference</p>
               <p className="text-2xl font-black font-mono">₹{difference.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</p>
            </div>
         </div>
      )}

      {errors.entries && <p className="text-xs font-black uppercase tracking-tighter text-rose-600 bg-rose-50 p-4 rounded-xl border border-rose-100">{errors.entries.message}</p>}
    </div>
  );
};
