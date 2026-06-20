import { z } from "zod";

export const partySchema = z.object({
  name: z.string().min(3, "Name must be at least 3 characters"),
  display_name: z.string().optional(),
  mobile: z.string().optional(),
  email: z.string().email("Invalid email").optional().or(z.literal("")),
  gstin: z.string().max(15, "Invalid GSTIN").optional().or(z.literal("")),
  pan: z.string().max(10, "Invalid PAN").optional().or(z.literal("")),
  address: z.string().optional(),
  credit_limit: z.coerce.number().min(0).default(0),
  is_customer: z.boolean().default(true),
  is_supplier: z.boolean().default(false),
  is_active: z.boolean().default(true),
});

export type PartyFormData = z.infer<typeof partySchema>;
