import { z } from "zod";
import { VoucherType } from "./types";

export const voucherEntrySchema = z.object({
  ledger_id: z.string().uuid("Invalid ledger"),
  debit_amount: z.coerce.number().min(0),
  credit_amount: z.coerce.number().min(0),
  narration: z.string().optional(),
}).refine(data => data.debit_amount > 0 || data.credit_amount > 0, {
  message: "Either debit or credit must be greater than zero",
  path: ["debit_amount"]
});

export const inventoryEntrySchema = z.object({
  stock_item_id: z.string().uuid("Invalid stock item"),
  quantity: z.coerce.number().gt(0, "Quantity must be positive"),
  rate: z.coerce.number().min(0),
  narration: z.string().optional(),
});

export const voucherSchema = z.object({
  voucher_type: z.nativeEnum(VoucherType),
  voucher_date: z.string(),
  narration: z.string().optional(),
  entries: z.array(voucherEntrySchema).min(2, "At least 2 accounting entries required"),
  inventory_entries: z.array(inventoryEntrySchema).optional().default([]),
}).refine(data => {
  const totalDebit = data.entries.reduce((sum, e) => sum + e.debit_amount, 0);
  const totalCredit = data.entries.reduce((sum, e) => sum + e.credit_amount, 0);
  return Math.abs(totalDebit - totalCredit) < 0.01;
}, {
  message: "Total Debit must equal Total Credit",
  path: ["entries"]
});

export type VoucherFormData = z.infer<typeof voucherSchema>;
