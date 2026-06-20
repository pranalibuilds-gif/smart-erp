"use client";

import { useFieldArray, useFormContext } from "react-hook-form";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Trash2, Plus } from "lucide-react";
import { VoucherFormData } from "../schemas";
import { useMasterStore } from "@/stores/master-store";
import { VoucherType } from "../types";

export const InventoryItemsTable = () => {
  const { control, register, watch } = useFormContext<VoucherFormData>();
  const { fields, append, remove } = useFieldArray({ control, name: "inventory_entries" });
  const { stockItems } = useMasterStore();
  const voucherType = watch("voucher_type");

  const inventorySupported = [VoucherType.SALES, VoucherType.PURCHASE, VoucherType.OPENING].includes(voucherType);

  if (!inventorySupported) return null;

  const inv_entries = watch("inventory_entries") || [];
  const totalAmount = inv_entries.reduce((sum, e) => sum + (Number(e.quantity) * Number(e.rate) || 0), 0);

  return (
    <div className="space-y-4 mb-8 p-4 bg-gray-50 rounded-lg border border-dashed">
      <h2 className="text-lg font-semibold">Inventory Transactions</h2>
      <div className="bg-white border rounded-md">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[40%]">Item</TableHead>
              <TableHead className="text-right">Quantity</TableHead>
              <TableHead className="text-right">Rate</TableHead>
              <TableHead className="text-right">Amount</TableHead>
              <TableHead className="w-[50px]"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {fields.map((field, index) => {
               const qty = watch(`inventory_entries.${index}.quantity`);
               const rate = watch(`inventory_entries.${index}.rate`);
               const amount = (Number(qty) * Number(rate)) || 0;

               return (
                <TableRow key={field.id}>
                  <TableCell>
                    <select
                      className="w-full h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
                      {...register(`inventory_entries.${index}.stock_item_id` as const)}
                    >
                      <option value="">Select Item</option>
                      {stockItems.map(i => (
                        <option key={i.id} value={i.id}>{i.name}</option>
                      ))}
                    </select>
                  </TableCell>
                  <TableCell>
                    <Input type="number" step="0.001" className="text-right" {...register(`inventory_entries.${index}.quantity` as const)} />
                  </TableCell>
                  <TableCell>
                    <Input type="number" step="0.01" className="text-right" {...register(`inventory_entries.${index}.rate` as const)} />
                  </TableCell>
                  <TableCell className="text-right font-mono">{amount.toFixed(2)}</TableCell>
                  <TableCell>
                    <Button variant="ghost" size="icon" onClick={() => remove(index)}>
                      <Trash2 className="h-4 w-4 text-red-500" />
                    </Button>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
          <TableHeader className="bg-gray-50 font-bold">
            <TableRow>
              <TableCell colSpan={3} className="text-right">Inventory Total</TableCell>
              <TableCell className="text-right font-mono text-green-600">{totalAmount.toFixed(2)}</TableCell>
              <TableCell></TableCell>
            </TableRow>
          </TableHeader>
        </Table>
      </div>
      <Button
        type="button"
        variant="outline"
        size="sm"
        onClick={() => append({ stock_item_id: "", quantity: 0, rate: 0 })}
      >
        <Plus className="mr-2 h-4 w-4" /> Add Item
      </Button>
    </div>
  );
};
