"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { registerSchema, RegisterData } from "../schemas";
import { useAuthStore } from "@/stores/auth-store";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Building2, ShieldCheck } from "lucide-react";

export const RegisterForm = () => {
  const registerUser = useAuthStore((state) => state.register);
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterData>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterData) => {
    setLoading(true);
    setError(null);
    try {
      await registerUser(data);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
      <Card className="w-full max-w-md shadow-xl border-none">
        <CardHeader className="space-y-1 text-center pb-8">
           <div className="flex justify-center mb-4">
              <div className="bg-blue-600 p-2 rounded-lg">
                 <Building2 className="text-white h-6 w-6" />
              </div>
           </div>
           <CardTitle className="text-2xl font-bold tracking-tight text-slate-900">Create Account</CardTitle>
           <CardDescription>Setup your administrative profile to manage your ERP</CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit(onSubmit)}>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="full_name">Legal Full Name</Label>
              <Input
                id="full_name"
                placeholder="e.g. Rahul Sharma"
                className="h-11 rounded-xl"
                {...register("full_name")}
              />
              {errors.full_name && <p className="text-xs text-red-500 font-bold uppercase tracking-tighter">{errors.full_name.message}</p>}
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Business Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="rahul@company.com"
                className="h-11 rounded-xl"
                {...register("email")}
              />
              {errors.email && <p className="text-xs text-red-500 font-bold uppercase tracking-tighter">{errors.email.message}</p>}
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Secure Password</Label>
              <Input id="password" type="password" className="h-11 rounded-xl" placeholder="••••••••" {...register("password")} />
              {errors.password && <p className="text-xs text-red-500 font-bold uppercase tracking-tighter">{errors.password.message}</p>}
            </div>

            <div className="p-3 bg-slate-50 rounded-xl border border-slate-100 flex items-start gap-3 mt-4">
               <ShieldCheck className="h-5 w-5 text-blue-600 shrink-0" />
               <p className="text-[10px] text-slate-500 leading-relaxed uppercase font-bold">Your data is secured with AES-256 encryption. By registering, you agree to our enterprise terms of service.</p>
            </div>

            {error && (
              <div className="bg-rose-50 text-rose-600 p-3 rounded-lg text-sm font-bold border border-rose-100 italic">
                {error}
              </div>
            )}
          </CardContent>
          <CardFooter className="flex flex-col space-y-4 pt-4 pb-10">
            <Button type="submit" className="w-full h-11 text-base font-bold bg-blue-600 hover:bg-blue-700 shadow-lg shadow-blue-600/20" disabled={loading}>
              {loading ? "Establishing Identity..." : "Finalize Registration"}
            </Button>
            <p className="text-sm text-slate-500">
              Already a member? <Link href="/login" className="text-blue-600 font-bold hover:underline">Login to Portal</Link>
            </p>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
};
