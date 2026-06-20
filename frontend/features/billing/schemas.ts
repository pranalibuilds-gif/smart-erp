import { z } from "zod";
import { DocumentType } from "./types";

export const invoiceItemSchema = z.object({
  stock_item_id: z.string().uuid("Invalid item").optional(),
  item_name: z.string().min(1, "Item name required"),
  item_code: z.string().optional(),
  unit_name: z.string().optional(),
  hsn_code: z.string().optional(),
  quantity: z.coerce.number().gt(0, "Quantity must be positive"),
  rate: z.coerce.number().min(0),
  tax_rate: z.coerce.number().min(0).default(0),
});

export const invoiceSchema = z.object({
  party_id: z.string().uuid("Invalid party"),
  document_type: z.nativeEnum(DocumentType),
  invoice_date: z.string(),
  narration: z.string().optional(),
  items: z.array(invoiceItemSchema).min(1, "At least 1 item required"),
});

export type InvoiceFormData = z.infer<typeof invoiceSchema>;
