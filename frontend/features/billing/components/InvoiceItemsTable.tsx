"use client";

import { useFieldArray, useFormContext } from "react-hook-form";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Trash2, Plus } from "lucide-react";
import { InvoiceFormData } from "../schemas";
import { useMasterStore } from "@/stores/master-store";
import { useEffect } from "react";

export const InvoiceItemsTable = () => {
  const { control, register, watch, setValue } = useFormContext<InvoiceFormData>();
  const { fields, append, remove } = useFieldArray({ control, name: "items" });
  const { stockItems, warehouses, fetchMasters } = useMasterStore();

  useEffect(() => {
    fetchMasters();
  }, [fetchMasters]);

  const items = watch("items") || [];
  const taxableTotal = items.reduce((sum, item) => sum + (Number(item.quantity) * Number(item.rate) || 0), 0);
  const taxTotal = items.reduce((sum, item) => {
    const taxable = Number(item.quantity) * Number(item.rate) || 0;
    return sum + (taxable * (Number(item.tax_rate) / 100));
  }, 0);

  const handleItemChange = (index: number, itemId: string) => {
    const stockItem = stockItems.find(i => i.id === itemId);
    if (stockItem) {
      setValue(`items.${index}.item_name`, stockItem.name);
      setValue(`items.${index}.rate`, stockItem.average_cost);
    }
  };

  return (
    <div className="space-y-4 mb-8">
      <h2 className="text-lg font-semibold">Items</h2>
      <div className="border rounded-md">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[30%]">Item</TableHead>
              <TableHead className="w-[15%]">Warehouse</TableHead>
              <TableHead className="text-right">Quantity</TableHead>
              <TableHead className="text-right">Rate</TableHead>
              <TableHead className="text-right">Tax %</TableHead>
              <TableHead className="text-right">Total</TableHead>
              <TableHead className="w-[50px]"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {fields.map((field, index) => {
               const qty = watch(`items.${index}.quantity`);
               const rate = watch(`items.${index}.rate`);
               const tax_rate = watch(`items.${index}.tax_rate`);
               const taxable = (Number(qty) * Number(rate)) || 0;
               const total = taxable + (taxable * (Number(tax_rate) / 100));

               return (
                <TableRow key={field.id}>
                  <TableCell>
                    <select
                      className="w-full h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm mb-1"
                      {...register(`items.${index}.stock_item_id` as const)}
                      onChange={(e) => handleItemChange(index, e.target.value)}
                    >
                      <option value="">Select Item</option>
                      {stockItems.map(i => (
                        <option key={i.id} value={i.id}>{i.name}</option>
                      ))}
                    </select>
                    <Input placeholder="Description" {...register(`items.${index}.item_name` as const)} />
                  </TableCell>
                  <TableCell>
                    <select
                      className="w-full h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm mb-1"
                      {...register(`items.${index}.warehouse_id` as const)}
                    >
                      <option value="">Warehouse</option>
                      {warehouses.map(w => (
                        <option key={w.id} value={w.id}>{w.name}</option>
                      ))}
                    </select>
                  </TableCell>
                  <TableCell>
                    <Input type="number" step="0.001" className="text-right" {...register(`items.${index}.quantity` as const)} />
                  </TableCell>
                  <TableCell>
                    <Input type="number" step="0.01" className="text-right" {...register(`items.${index}.rate` as const)} />
                  </TableCell>
                  <TableCell>
                    <Input type="number" step="1" className="text-right" {...register(`items.${index}.tax_rate` as const)} />
                  </TableCell>
                  <TableCell className="text-right font-mono font-bold">
                    {total.toFixed(2)}
                  </TableCell>
                  <TableCell>
                    <Button variant="ghost" size="icon" onClick={() => remove(index)}>
                      <Trash2 className="h-4 w-4 text-red-500" />
                    </Button>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>

      <div className="flex justify-between items-start">
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={() => append({ item_name: "", quantity: 1, rate: 0, tax_rate: 18 })}
        >
          <Plus className="mr-2 h-4 w-4" /> Add Line Item
        </Button>

        <div className="w-64 space-y-2 text-sm">
          <div className="flex justify-between">
             <span className="text-gray-500">Taxable Amount:</span>
             <span className="font-mono">₹{taxableTotal.toFixed(2)}</span>
          </div>
          <div className="flex justify-between">
             <span className="text-gray-500">Tax Total:</span>
             <span className="font-mono">₹{taxTotal.toFixed(2)}</span>
          </div>
          <div className="flex justify-between text-lg font-bold border-t pt-2">
             <span>Grand Total:</span>
             <span className="text-blue-600 font-mono">₹{(taxableTotal + taxTotal).toFixed(2)}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
