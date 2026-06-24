"use client";

import { useEffect, useState } from "react";
import { useCompanyStore } from "@/stores/company-store";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Building2, Save, Globe, MapPin, Phone, Mail, Fingerprint, ShieldCheck } from "lucide-react";
import { useForm } from "react-hook-form";

export default function CompanySettingsPage() {
  const { activeCompany, updateCompany, isLoading } = useCompanyStore();
  const [success, setSuccess] = useState(false);

  const { register, handleSubmit, reset } = useForm({
    defaultValues: activeCompany || {}
  });

  useEffect(() => {
    if (activeCompany) reset(activeCompany);
  }, [activeCompany, reset]);

  const onSubmit = async (data: any) => {
    if (!activeCompany) return;
    try {
      await updateCompany(activeCompany.id, data);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      alert("Failed to update corporate profile");
    }
  };

  if (!activeCompany) return <div className="p-10 text-center font-bold text-slate-400">SELECT A COMPANY TO CONFIGURE PROTOCOLS</div>;

  return (
    <div className="p-10 max-w-4xl mx-auto space-y-10 pb-32 animate-in fade-in duration-700">
      <div className="flex justify-between items-end border-b border-slate-200 pb-10">
        <div className="flex items-center gap-6">
          <div className="bg-slate-900 p-4 rounded-[24px] shadow-2xl shadow-slate-900/20 text-white ring-8 ring-slate-100">
            <Building2 className="h-8 w-8" />
          </div>
          <div>
            <h1 className="text-4xl font-black tracking-tighter text-slate-900 uppercase italic">Corporate Identity</h1>
            <p className="text-slate-400 font-bold uppercase tracking-widest mt-1 italic">Configure master metadata and legal parameters</p>
          </div>
        </div>
        <Button
           onClick={handleSubmit(onSubmit)}
           disabled={isLoading}
           className="bg-blue-600 hover:bg-blue-700 h-14 px-10 rounded-2xl font-black uppercase tracking-widest shadow-2xl shadow-blue-500/40 transition-all active:scale-95"
        >
           {isLoading ? "Syncing..." : <><Save className="mr-2 h-5 w-5" /> Commit Changes</>}
        </Button>
      </div>

      {success && (
        <div className="p-4 bg-emerald-500 text-white rounded-2xl font-black uppercase tracking-widest text-center shadow-xl shadow-emerald-500/20 animate-in zoom-in-95">
           Identity Record Successfully Updated
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="grid grid-cols-1 md:grid-cols-2 gap-8">
         <Card className="border-none shadow-sm ring-1 ring-slate-200 rounded-[32px] overflow-hidden">
            <CardHeader className="bg-slate-50/50 border-b px-8 py-6">
               <CardTitle className="text-sm font-black uppercase tracking-[0.2em] flex items-center gap-3">
                  <Fingerprint className="h-4 w-4 text-blue-600" /> Basic Metadata
               </CardTitle>
            </CardHeader>
            <CardContent className="p-8 space-y-6">
               <div className="space-y-2">
                  <Label className="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-1">Trade Name</Label>
                  <Input className="h-12 rounded-xl border-slate-200 font-bold" {...register("name")} />
               </div>
               <div className="space-y-2">
                  <Label className="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-1">Legal Registered Entity</Label>
                  <Input className="h-12 rounded-xl border-slate-200 font-bold" {...register("legal_name")} />
               </div>
               <div className="space-y-2">
                  <Label className="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-1">System Slug (Read-only)</Label>
                  <Input className="h-12 rounded-xl border-slate-200 font-mono bg-slate-50 text-slate-400" {...register("slug")} disabled />
               </div>
            </CardContent>
         </Card>

         <Card className="border-none shadow-sm ring-1 ring-slate-200 rounded-[32px] overflow-hidden">
            <CardHeader className="bg-slate-50/50 border-b px-8 py-6">
               <CardTitle className="text-sm font-black uppercase tracking-[0.2em] flex items-center gap-3">
                  <ShieldCheck className="h-4 w-4 text-emerald-600" /> Compliance & Tax
               </CardTitle>
            </CardHeader>
            <CardContent className="p-8 space-y-6">
               <div className="space-y-2">
                  <Label className="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-1">GST / Tax Identification</Label>
                  <Input className="h-12 rounded-xl border-slate-200 font-mono font-black uppercase tracking-tighter" {...register("gst_number")} />
               </div>
               <div className="space-y-2">
                  <Label className="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-1">Primary Jurisdiction</Label>
                  <Input className="h-12 rounded-xl border-slate-200 font-bold" {...register("state")} />
               </div>
               <div className="space-y-2">
                  <Label className="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-1">Operational Country</Label>
                  <Input className="h-12 rounded-xl border-slate-200 font-bold" {...register("country")} />
               </div>
            </CardContent>
         </Card>

         <Card className="border-none shadow-sm ring-1 ring-slate-200 rounded-[32px] overflow-hidden md:col-span-2">
            <CardHeader className="bg-slate-50/50 border-b px-8 py-6">
               <CardTitle className="text-sm font-black uppercase tracking-[0.2em] flex items-center gap-3">
                  <MapPin className="h-4 w-4 text-rose-600" /> Headquarters Address & Communication
               </CardTitle>
            </CardHeader>
            <CardContent className="p-8 grid grid-cols-1 md:grid-cols-2 gap-8">
               <div className="space-y-6">
                  <div className="space-y-2">
                     <Label className="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-1">Full Physical Address</Label>
                     <textarea
                        className="w-full min-h-[120px] p-4 rounded-2xl border border-slate-200 font-bold text-sm outline-none focus:ring-4 focus:ring-blue-50 transition-all"
                        {...register("address")}
                     />
                  </div>
               </div>
               <div className="space-y-6">
                  <div className="space-y-2">
                     <Label className="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-1">Official Email Node</Label>
                     <div className="relative">
                        <Mail className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-300" />
                        <Input className="h-12 pl-12 rounded-xl border-slate-200 font-bold" {...register("email")} />
                     </div>
                  </div>
                  <div className="space-y-2">
                     <Label className="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-1">Corporate Contact Line</Label>
                     <div className="relative">
                        <Phone className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-300" />
                        <Input className="h-12 pl-12 rounded-xl border-slate-200 font-bold" {...register("phone")} />
                     </div>
                  </div>
               </div>
            </CardContent>
         </Card>
      </form>
    </div>
  );
}
