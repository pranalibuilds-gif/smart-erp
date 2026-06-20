"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { partySchema, PartyFormData } from "@/features/parties/schemas";
import { usePartyStore } from "@/stores/party-store";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { useState } from "react";
import { Checkbox } from "@/components/ui/checkbox";

export default function NewPartyPage() {
  const { createParty } = usePartyStore();
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<PartyFormData>({
    resolver: zodResolver(partySchema),
    defaultValues: {
      is_customer: true,
      is_supplier: false,
      is_active: true,
      credit_limit: 0,
    }
  });

  const isCustomer = watch("is_customer");
  const isSupplier = watch("is_supplier");

  const onSubmit = async (data: PartyFormData) => {
    setLoading(true);
    setError(null);
    try {
      await createParty(data);
      router.push("/parties");
    } catch (err: any) {
      setError(err.message || "Failed to create party");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl font-bold">New Party</CardTitle>
          <CardDescription>Add a new customer or supplier to your records</CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit(onSubmit)}>
          <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label htmlFor="name">Business Name / Name</Label>
              <Input id="name" placeholder="ABC Corp" {...register("name")} />
              {errors.name && <p className="text-xs text-red-500">{errors.name.message}</p>}
            </div>
            <div className="space-y-2">
              <Label htmlFor="display_name">Display Name (Optional)</Label>
              <Input id="display_name" placeholder="ABC" {...register("display_name")} />
            </div>

            <div className="space-y-2">
              <Label htmlFor="mobile">Mobile Number</Label>
              <Input id="mobile" placeholder="+91 9876543210" {...register("mobile")} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email Address</Label>
              <Input id="email" type="email" placeholder="contact@abc.com" {...register("email")} />
            </div>

            <div className="space-y-2">
              <Label htmlFor="gstin">GSTIN</Label>
              <Input id="gstin" placeholder="27AAAAA0000A1Z5" {...register("gstin")} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="pan">PAN</Label>
              <Input id="pan" placeholder="ABCDE1234F" {...register("pan")} />
            </div>

            <div className="md:col-span-2 space-y-2">
              <Label htmlFor="address">Full Address</Label>
              <Input id="address" placeholder="Unit 1, Business Tower..." {...register("address")} />
            </div>

            <div className="space-y-2">
              <Label htmlFor="credit_limit">Credit Limit</Label>
              <Input id="credit_limit" type="number" step="0.01" {...register("credit_limit")} />
            </div>

            <div className="flex items-center space-x-6 pt-4">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="is_customer"
                  checked={isCustomer}
                  onCheckedChange={(checked) => setValue("is_customer", !!checked)}
                />
                <Label htmlFor="is_customer" className="text-sm font-medium">Customer</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="is_supplier"
                  checked={isSupplier}
                  onCheckedChange={(checked) => setValue("is_supplier", !!checked)}
                />
                <Label htmlFor="is_supplier" className="text-sm font-medium">Supplier</Label>
              </div>
            </div>

            {error && <p className="md:col-span-2 text-sm text-red-500 font-medium">{error}</p>}
          </CardContent>
          <CardFooter className="flex justify-between">
            <Button type="button" variant="outline" onClick={() => router.back()}>Cancel</Button>
            <Button type="submit" disabled={loading}>
              {loading ? "Creating..." : "Save Party"}
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
