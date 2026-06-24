"use client";

import { useEffect, useState } from "react";
import apiClient from "@/lib/api-client";
import { useCompanyStore } from "@/stores/company-store";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button, buttonVariants } from "@/components/ui/button";
import { Building2, Plus, ArrowRight, CheckCircle2, MoreVertical, Settings, Users, ShieldCheck, MapPin, Globe } from "lucide-react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

export default function CompanySelectPage() {
  const [companies, setCompanies] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const setCompany = useCompanyStore((state) => state.setActiveCompany);
  const router = useRouter();

  useEffect(() => {
    apiClient.get("/api/v1/companies")
      .then((res) => setCompanies(res.data.data))
      .finally(() => setLoading(false));
  }, []);

  const handleSelect = (company: any) => {
    setCompany(company);
    router.push("/dashboard");
  };

  return (
    <div className="min-h-screen bg-white flex flex-col items-center justify-center p-8 pb-20 relative overflow-hidden">
      {/* Decorative patterns */}
      <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-blue-50 rounded-full translate-x-1/2 -translate-y-1/2 blur-3xl opacity-60" />
      <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-slate-50 rounded-full -translate-x-1/2 translate-y-1/2 blur-3xl opacity-60" />

      <div className="w-full max-w-5xl space-y-12 relative z-10 animate-in fade-in slide-in-from-top-4 duration-1000">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-8 border-b border-slate-100 pb-12">
          <div className="space-y-4">
            <div className="bg-blue-600 w-16 h-16 rounded-[22px] flex items-center justify-center shadow-2xl shadow-blue-500/40 ring-8 ring-blue-50 mb-6 text-white rotate-3">
              <Building2 className="h-8 w-8" />
            </div>
            <h1 className="text-5xl font-black tracking-tighter text-slate-900 uppercase leading-none">Your Command Center</h1>
            <p className="text-lg font-bold text-slate-400 uppercase tracking-widest mt-2 flex items-center gap-3">
               Select operational workspace <ArrowRight className="h-5 w-5 text-blue-500 animate-pulse" />
            </p>
          </div>
          <Link href="/company/create" className={cn(buttonVariants(), "bg-blue-600 hover:bg-blue-700 h-16 px-10 rounded-2xl font-black uppercase tracking-widest shadow-2xl shadow-blue-600/30 ring-4 ring-blue-100 transition-all active:scale-95")}>
            <Plus className="mr-3 h-5 w-5 stroke-[4]" /> Onboard New Entity
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
          {companies.map((company) => (
            <Card
              key={company.id}
              className="group cursor-pointer border-none shadow-[0_8px_30px_rgb(0,0,0,0.04)] ring-1 ring-slate-200 hover:ring-blue-600 hover:shadow-[0_20px_50px_rgba(37,99,235,0.15)] transition-all duration-500 overflow-hidden rounded-[40px] bg-white relative p-4"
              onClick={() => handleSelect(company)}
            >
              <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 group-hover:scale-110 transition-all duration-700 pointer-events-none">
                 <Building2 className="h-32 w-32 text-slate-900 stroke-[1]" />
              </div>

              <CardHeader className="flex flex-row items-start justify-between pb-4 pt-6 px-6">
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                     <Badge variant="outline" className="bg-blue-50 text-blue-600 border-blue-200 font-black text-[9px] uppercase tracking-widest px-2.5 py-0.5 rounded-lg shadow-sm">HQ / PRIMARY</Badge>
                  </div>
                  <CardTitle className="text-2xl font-black tracking-tight text-slate-900 group-hover:text-blue-600 transition-colors uppercase italic">{company.name}</CardTitle>
                  <div className="flex items-center gap-3 text-slate-400">
                     <span className="text-[10px] font-black uppercase tracking-[0.2em]">{company.slug}</span>
                     <div className="w-1 h-1 rounded-full bg-slate-300" />
                     <span className="text-[10px] font-black uppercase tracking-[0.2em]">Tier-1 Subscription</span>
                  </div>
                </div>
                <div className="bg-emerald-500/10 h-10 w-10 rounded-2xl flex items-center justify-center border border-emerald-500/20">
                   <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_#10b981] animate-pulse" />
                </div>
              </CardHeader>
              <CardContent className="px-6 pb-6 space-y-8">
                <div className="grid grid-cols-2 gap-4">
                   <div className="p-4 bg-slate-50/80 rounded-2xl border border-slate-100/60 group-hover:bg-blue-50/50 group-hover:border-blue-100 transition-colors">
                      <div className="flex items-center gap-2 mb-1.5 opacity-40 group-hover:opacity-100 transition-opacity">
                         <ShieldCheck className="h-3 w-3 text-blue-600" />
                         <span className="text-[9px] font-black uppercase tracking-widest text-slate-500">Security</span>
                      </div>
                      <p className="text-xs font-bold text-slate-900 uppercase">Vault-Encrypted</p>
                   </div>
                   <div className="p-4 bg-slate-50/80 rounded-2xl border border-slate-100/60 group-hover:bg-blue-50/50 group-hover:border-blue-100 transition-colors">
                      <div className="flex items-center gap-2 mb-1.5 opacity-40 group-hover:opacity-100 transition-opacity">
                         <Globe className="h-3 w-3 text-blue-600" />
                         <span className="text-[9px] font-black uppercase tracking-widest text-slate-500">Region</span>
                      </div>
                      <p className="text-xs font-bold text-slate-900 uppercase">Western Zone</p>
                   </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                     <div className="flex -space-x-3">
                        {[1, 2, 3].map(i => (
                           <div key={i} className="h-9 w-9 rounded-[14px] bg-white border-2 border-white flex items-center justify-center shadow-lg shadow-slate-900/5 ring-1 ring-slate-100 overflow-hidden">
                              <img src={`https://i.pravatar.cc/100?img=${i+10}`} className="h-full w-full object-cover" alt="user" />
                           </div>
                        ))}
                     </div>
                     <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">+14 Core Members</p>
                  </div>
                  <div className="flex gap-2">
                     <Link href="/settings/company" className={cn(buttonVariants({ variant: "ghost", size: "icon" }), "h-12 w-12 rounded-[18px] text-slate-400 hover:text-blue-600 hover:bg-blue-50 hover:shadow-inner transition-all")}>
                        <Settings className="h-5 w-5" />
                     </Link>
                     <div className="h-12 w-12 rounded-[18px] bg-slate-900 text-white flex items-center justify-center group-hover:bg-blue-600 shadow-xl group-hover:shadow-blue-600/30 transition-all group-hover:translate-x-1">
                        <ArrowRight className="h-5 w-5" />
                     </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}

          {companies.length === 0 && !loading && (
            <Card className="col-span-2 py-32 border-dashed border-4 rounded-[60px] bg-slate-50/30 flex flex-col items-center gap-8 text-center ring-8 ring-white shadow-2xl">
               <div className="bg-white p-8 rounded-[32px] shadow-xl shadow-slate-200/50 animate-bounce duration-[3s]">
                  <Building2 className="h-20 w-20 text-slate-200 stroke-[1.5]" />
               </div>
               <div>
                  <h3 className="text-3xl font-black text-slate-900 uppercase tracking-tighter italic">Workspace Protocol: Ready</h3>
                  <p className="text-slate-400 font-bold uppercase tracking-widest max-w-sm mt-2">Initialize your first entity profile to enable accounting modules.</p>
               </div>
               <Link href="/company/create" className={cn(buttonVariants(), "h-16 px-12 rounded-2xl bg-slate-900 text-white hover:bg-blue-600 font-black uppercase tracking-widest shadow-2xl transition-all")}>Initialize System</Link>
            </Card>
          )}
        </div>
      </div>

      <div className="fixed bottom-0 left-0 right-0 p-10 flex justify-center pointer-events-none">
         <div className="bg-slate-900 px-8 py-3 rounded-full flex items-center gap-4 border border-white/10 shadow-2xl shadow-slate-900/40">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            <p className="text-[10px] font-black text-white uppercase tracking-[0.4em]">SmartERP Protocol v1.0.4 RC-Prime • Secure Enterprise Channel</p>
         </div>
      </div>
    </div>
  );
}
