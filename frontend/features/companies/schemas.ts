import { z } from "zod";

export const companyCreateSchema = z.object({
  name: z.string().min(3, "Company name must be at least 3 characters"),
  legal_name: z.string().min(3, "Legal name must be at least 3 characters"),
  email: z.string().email("Invalid email address").optional().or(z.literal("")),
  phone: z.string().optional(),
  address: z.string().optional(),
  state: z.string().optional(),
  country: z.string().default("India"),
  gst_number: z.string().optional(),
  financial_year_start: z.string().refine((val) => !isNaN(Date.parse(val)), {
    message: "Invalid date",
  }),
});

export type CompanyCreateData = z.infer<typeof companyCreateSchema>;
