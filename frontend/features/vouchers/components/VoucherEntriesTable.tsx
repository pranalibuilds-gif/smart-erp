"use client";

import { useFieldArray, useFormContext } from "react-hook-form";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Trash2, Plus } from "lucide-react";
import { VoucherFormData } from "../schemas";
import { useMasterStore } from "@/stores/master-store";
import { useEffect } from "react";

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

  return (
    <div className="space-y-4 mb-8">
      <h2 className="text-lg font-semibold">Accounting Entries</h2>
      <div className="border rounded-md">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[40%]">Ledger</TableHead>
              <TableHead className="text-right">Debit</TableHead>
              <TableHead className="text-right">Credit</TableHead>
              <TableHead className="w-[50px]"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {fields.map((field, index) => (
              <TableRow key={field.id}>
                <TableCell>
                  <select
                    className="w-full h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors"
                    {...register(`entries.${index}.ledger_id` as const)}
                  >
                    <option value="">Select Ledger</option>
                    {ledgers.map(l => (
                      <option key={l.id} value={l.id}>{l.name}</option>
                    ))}
                  </select>
                </TableCell>
                <TableCell>
                  <Input
                    type="number"
                    step="0.01"
                    className="text-right"
                    {...register(`entries.${index}.debit_amount` as const)}
                  />
                </TableCell>
                <TableCell>
                  <Input
                    type="number"
                    step="0.01"
                    className="text-right"
                    {...register(`entries.${index}.credit_amount` as const)}
                  />
                </TableCell>
                <TableCell>
                  <Button variant="ghost" size="icon" onClick={() => remove(index)}>
                    <Trash2 className="h-4 w-4 text-red-500" />
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
          <TableHeader className="bg-gray-50 font-bold">
            <TableRow>
              <TableCell className="text-right">Totals</TableCell>
              <TableCell className="text-right font-mono text-blue-600">{totalDebit.toFixed(2)}</TableCell>
              <TableCell className="text-right font-mono text-purple-600">{totalCredit.toFixed(2)}</TableCell>
              <TableCell></TableCell>
            </TableRow>
          </TableHeader>
        </Table>
      </div>
      <Button
        type="button"
        variant="outline"
        size="sm"
        onClick={() => append({ ledger_id: "", debit_amount: 0, credit_amount: 0 })}
      >
        <Plus className="mr-2 h-4 w-4" /> Add Entry
      </Button>
      {errors.entries && <p className="text-sm text-red-500">{errors.entries.message}</p>}
    </div>
  );
};
