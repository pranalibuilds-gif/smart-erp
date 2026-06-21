"use client";

import { useForm, FormProvider, useFieldArray } from "react-hook-form";
import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import { useMasterStore } from "@/stores/master-store";
import { createTransfer } from "@/features/inventory/api/inventory-api";
import { Card, CardContent } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Trash2, Plus } from "lucide-react";

export default function NewTransferPage() {
  const router = useRouter();
  const { warehouses, stockItems, fetchMasters } = useMasterStore();
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchMasters();
  }, [fetchMasters]);

  const methods = useForm({
    defaultValues: {
      from_warehouse_id: "",
      to_warehouse_id: "",
      transfer_date: new Date().toISOString().split('T')[0],
      notes: "",
      items: [{ stock_item_id: "", quantity: 0 }]
    }
  });

  const { fields, append, remove } = useFieldArray({ control: methods.control, name: "items" });

  const onSubmit = async (data: any) => {
    setLoading(true);
    try {
      await createTransfer(data);
      router.push("/inventory/transfers");
    } catch (err: any) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">New Stock Transfer</h1>

      <FormProvider {...methods}>
        <form onSubmit={methods.handleSubmit(onSubmit)}>
          <Card>
            <CardContent className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                <div className="space-y-2">
                  <Label>From Warehouse (Source)</Label>
                  <select
                    className="w-full h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                    {...methods.register("from_warehouse_id")}
                  >
                    <option value="">Select Warehouse</option>
                    {warehouses.map(w => <option key={w.id} value={w.id}>{w.name}</option>)}
                  </select>
                </div>
                <div className="space-y-2">
                  <Label>To Warehouse (Destination)</Label>
                  <select
                    className="w-full h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                    {...methods.register("to_warehouse_id")}
                  >
                    <option value="">Select Warehouse</option>
                    {warehouses.map(w => <option key={w.id} value={w.id}>{w.name}</option>)}
                  </select>
                </div>
                <div className="space-y-2">
                  <Label>Date</Label>
                  <Input type="date" {...methods.register("transfer_date")} />
                </div>
                <div className="space-y-2">
                  <Label>Notes</Label>
                  <Input placeholder="Optional notes" {...methods.register("notes")} />
                </div>
              </div>

              <div className="mb-8">
                <h2 className="text-lg font-semibold mb-4">Stock Items</h2>
                <div className="border rounded-md">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="w-[60%]">Item</TableHead>
                        <TableHead className="text-right">Quantity</TableHead>
                        <TableHead className="w-[50px]"></TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {fields.map((field, index) => (
                        <TableRow key={field.id}>
                          <TableCell>
                            <select
                              className="w-full h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                              {...methods.register(`items.${index}.stock_item_id` as const)}
                            >
                              <option value="">Select Item</option>
                              {stockItems.map(i => <option key={i.id} value={i.id}>{i.name}</option>)}
                            </select>
                          </TableCell>
                          <TableCell>
                            <Input type="number" step="0.001" className="text-right" {...methods.register(`items.${index}.quantity` as const)} />
                          </TableCell>
                          <TableCell>
                            <Button variant="ghost" size="icon" onClick={() => remove(index)}><Trash2 className="h-4 w-4 text-red-500" /></Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
                <Button type="button" variant="outline" size="sm" className="mt-4" onClick={() => append({ stock_item_id: "", quantity: 0 })}>
                  <Plus className="mr-2 h-4 w-4" /> Add Item
                </Button>
              </div>

              <div className="flex justify-end gap-4 border-t pt-4">
                <Button variant="outline" type="button" onClick={() => router.back()}>Cancel</Button>
                <Button type="submit" disabled={loading}>Save Transfer</Button>
              </div>
            </CardContent>
          </Card>
        </form>
      </FormProvider>
    </div>
  );
}
