"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { loginSchema, LoginCredentials } from "../schemas";
import { useAuthStore } from "@/stores/auth-store";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Building2, ShieldCheck, Lock, Mail, ChevronRight } from "lucide-react";

export const LoginForm = () => {
  const login = useAuthStore((state) => state.login);
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginCredentials>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginCredentials) => {
    setLoading(true);
    setError(null);
    try {
      await login(data);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Invalid authentication parameters");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#f8fafc] p-6 relative overflow-hidden">
      {/* Decorative patterns */}
      <div className="absolute top-0 left-0 w-[500px] h-[500px] bg-blue-100/50 rounded-full -translate-x-1/2 -translate-y-1/2 blur-3xl" />
      <div className="absolute bottom-0 right-0 w-[500px] h-[500px] bg-indigo-100/50 rounded-full translate-x-1/2 translate-y-1/2 blur-3xl" />

      <Card className="w-full max-w-[440px] shadow-[0_32px_64px_-12px_rgba(0,0,0,0.14)] border-none ring-1 ring-slate-200/60 rounded-[32px] overflow-hidden relative bg-white/90 backdrop-blur-xl animate-in zoom-in-95 duration-500">
        <CardHeader className="space-y-4 text-center pb-10 pt-12 px-10">
          <div className="flex justify-center mb-4">
             <div className="bg-blue-600 h-16 w-16 rounded-[22px] flex items-center justify-center shadow-xl shadow-blue-500/30 ring-4 ring-blue-50">
                <Building2 className="text-white h-8 w-8" />
             </div>
          </div>
          <div className="space-y-1">
             <CardTitle className="text-3xl font-black tracking-tighter text-slate-900 uppercase">SmartERP</CardTitle>
             <CardDescription className="text-lg font-bold text-slate-500">Welcome Back!</CardDescription>
          </div>
        </CardHeader>
        <form onSubmit={handleSubmit(onSubmit)} className="px-4 pb-4">
          <CardContent className="space-y-6 px-6">
            <div className="space-y-2.5">
              <Label htmlFor="email" className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-400 ml-1">Corporate Email</Label>
              <div className="relative group">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400 group-focus-within:text-blue-500 transition-colors" />
                <Input
                  id="email"
                  type="email"
                  placeholder="admin@smarterp.io"
                  className="h-14 pl-12 rounded-2xl border-slate-200 bg-slate-50/50 focus:bg-white focus:ring-4 focus:ring-blue-50 transition-all font-semibold"
                  {...register("email")}
                />
              </div>
              {errors.email && <p className="text-[10px] text-rose-600 font-black uppercase tracking-tighter ml-1">{errors.email.message}</p>}
            </div>

            <div className="space-y-2.5">
              <div className="flex justify-between items-center ml-1">
                <Label htmlFor="password" title="password" className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-400">Master Password</Label>
                <button type="button" className="text-[10px] font-black text-blue-600 uppercase tracking-widest hover:underline">Reset?</button>
              </div>
              <div className="relative group">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400 group-focus-within:text-blue-500 transition-colors" />
                <Input id="password" type="password" placeholder="••••••••" className="h-14 pl-12 rounded-2xl border-slate-200 bg-slate-50/50 focus:bg-white focus:ring-4 focus:ring-blue-50 transition-all font-semibold" {...register("password")} />
              </div>
              {errors.password && <p className="text-[10px] text-rose-600 font-black uppercase tracking-tighter ml-1">{errors.password.message}</p>}
            </div>

            {error && (
              <div className="bg-rose-50 border border-rose-100 p-4 rounded-2xl flex items-center gap-3 text-rose-600 animate-in slide-in-from-top-2">
                 <ShieldCheck className="h-5 w-5 shrink-0" />
                 <p className="text-xs font-black uppercase tracking-tighter">{error}</p>
              </div>
            )}
          </CardContent>
          <CardFooter className="flex flex-col space-y-6 pt-6 pb-12 px-6">
            <Button type="submit" className="w-full h-14 text-base font-black uppercase tracking-widest bg-blue-600 hover:bg-blue-700 shadow-2xl shadow-blue-500/40 rounded-2xl group transition-all" disabled={loading}>
              {loading ? "Authenticating..." : (
                <div className="flex items-center gap-2">
                   Identify & Login
                   <ChevronRight className="h-4 w-4 group-hover:translate-x-1 transition-all" />
                </div>
              )}
            </Button>
            <div className="text-center">
               <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">
                  First time here? <Link href="/register" className="text-blue-600 font-black hover:underline decoration-blue-600/30 decoration-2 underline-offset-4 ml-1">Create Access</Link>
               </p>
            </div>
          </CardFooter>
        </form>
        <div className="bg-slate-50 py-4 px-10 text-center border-t border-slate-100 flex items-center justify-center gap-2">
           <ShieldCheck className="h-3 w-3 text-slate-400 font-bold" />
           <p className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">Secured by VaultGuard v2.4</p>
        </div>
      </Card>
    </div>
  );
};
