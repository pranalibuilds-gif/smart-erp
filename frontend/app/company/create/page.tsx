"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { companyCreateSchema, CompanyCreateData } from "@/features/companies/schemas";
import { useCompanyStore } from "@/stores/company-store";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { useState } from "react";

export default function CompanyCreatePage() {
  const { createCompany, setActiveCompany } = useCompanyStore();
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CompanyCreateData>({
    resolver: zodResolver(companyCreateSchema),
    defaultValues: {
      country: "India",
      financial_year_start: new Date(new Date().getFullYear(), 3, 1).toISOString().split('T')[0], // Default to April 1st of current year
    }
  });

  const onSubmit = async (data: CompanyCreateData) => {
    setLoading(true);
    setError(null);
    try {
      const company = await createCompany(data);
      setActiveCompany(company);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Failed to create company");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 bg-gray-50">
      <Card className="w-full max-w-2xl">
        <CardHeader>
          <CardTitle className="text-2xl font-bold">Create Company</CardTitle>
          <CardDescription>Setup your company profile and first financial year</CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit(onSubmit)}>
          <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name">Display Name</Label>
              <Input id="name" placeholder="Smart ERP Solutions" {...register("name")} />
              {errors.name && <p className="text-xs text-red-500">{errors.name.message}</p>}
            </div>
            <div className="space-y-2">
              <Label htmlFor="legal_name">Legal Name</Label>
              <Input id="legal_name" placeholder="Smart ERP Solutions Pvt Ltd" {...register("legal_name")} />
              {errors.legal_name && <p className="text-xs text-red-500">{errors.legal_name.message}</p>}
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" placeholder="contact@company.com" {...register("email")} />
              {errors.email && <p className="text-xs text-red-500">{errors.email.message}</p>}
            </div>
            <div className="space-y-2">
              <Label htmlFor="financial_year_start">Financial Year Start</Label>
              <Input id="financial_year_start" type="date" {...register("financial_year_start")} />
              {errors.financial_year_start && <p className="text-xs text-red-500">{errors.financial_year_start.message}</p>}
            </div>
            <div className="space-y-2">
              <Label htmlFor="state">State</Label>
              <Input id="state" placeholder="Maharashtra" {...register("state")} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="country">Country</Label>
              <Input id="country" {...register("country")} />
            </div>
            <div className="md:col-span-2 space-y-2">
              <Label htmlFor="address">Address</Label>
              <Input id="address" placeholder="123 Business Park" {...register("address")} />
            </div>
            {error && <p className="md:col-span-2 text-sm text-red-500 font-medium">{error}</p>}
          </CardContent>
          <CardFooter className="flex justify-between">
            <Button type="button" variant="outline" onClick={() => router.back()}>Cancel</Button>
            <Button type="submit" disabled={loading}>
              {loading ? "Creating..." : "Create Company"}
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
