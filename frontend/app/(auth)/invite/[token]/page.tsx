"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Building2, ShieldCheck, CheckCircle2, UserPlus, ArrowRight, Lock } from "lucide-react";
import Link from "next/link";
import { cn } from "@/lib/utils";

export default function InvitationPage() {
  const { token } = useParams();
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  const handleAccept = () => {
    setLoading(true);
    // Simulation of acceptance
    setTimeout(() => {
       router.push("/login");
    }, 1500);
  };

  return (
    <div className="min-h-screen bg-[#f8fafc] flex items-center justify-center p-6 relative overflow-hidden">
       {/* High-impact background effects */}
      <div className="absolute top-0 right-0 w-[800px] h-[800px] bg-blue-100/40 rounded-full translate-x-1/2 -translate-y-1/2 blur-[120px] animate-pulse" />
      <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-indigo-100/40 rounded-full -translate-x-1/2 translate-y-1/2 blur-[100px]" />

      <Card className="w-full max-w-[500px] shadow-[0_40px_100px_-20px_rgba(0,0,0,0.15)] border-none ring-1 ring-slate-200/60 rounded-[40px] overflow-hidden relative bg-white/95 backdrop-blur-2xl animate-in zoom-in-95 slide-in-from-bottom-8 duration-700">
        <div className="bg-slate-900 h-2 w-full" />

        <CardHeader className="space-y-6 text-center pb-10 pt-16 px-10">
          <div className="flex justify-center mb-6">
             <div className="relative group">
                <div className="absolute inset-0 bg-blue-600 rounded-[28px] blur-2xl opacity-20 group-hover:opacity-40 transition-opacity duration-500" />
                <div className="bg-blue-600 h-24 w-24 rounded-[32px] flex items-center justify-center shadow-2xl shadow-blue-500/40 ring-8 ring-blue-50 relative z-10 rotate-3 group-hover:rotate-0 transition-transform duration-500">
                   <UserPlus className="text-white h-10 w-10 stroke-[2.5]" />
                </div>
             </div>
          </div>
          <div className="space-y-2">
             <h3 className="text-[10px] font-black uppercase tracking-[0.4em] text-blue-600">Access Invitation</h3>
             <CardTitle className="text-4xl font-black tracking-tighter text-slate-900 uppercase italic">Join the Workforce</CardTitle>
             <CardDescription className="text-lg font-bold text-slate-400">Collaborative Cloud accounting protocol</CardDescription>
          </div>
        </CardHeader>

        <CardContent className="px-10 pb-6 space-y-10">
           <div className="p-8 bg-slate-50 rounded-[32px] border border-slate-100 relative group overflow-hidden transition-all hover:bg-blue-50/30 hover:border-blue-100">
              <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity duration-700">
                 <Building2 className="h-20 w-20 text-slate-900" />
              </div>

              <div className="flex flex-col items-center gap-6 relative z-10 text-center">
                 <div className="space-y-1">
                    <p className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-400">Inviting Organization</p>
                    <h4 className="text-2xl font-black text-slate-900 tracking-tight italic">Nexus Industrial Solutions</h4>
                 </div>

                 <div className="flex items-center gap-2 bg-white px-5 py-2 rounded-2xl shadow-sm border border-slate-100">
                    <ShieldCheck className="h-4 w-4 text-emerald-500" />
                    <span className="text-xs font-black uppercase tracking-widest text-slate-700">Role: Accountant</span>
                 </div>
              </div>
           </div>

           <div className="flex items-start gap-4 px-2">
              <div className="h-10 w-10 rounded-xl bg-blue-50 border border-blue-100 flex items-center justify-center shrink-0">
                 <Lock className="h-5 w-5 text-blue-600" />
              </div>
              <p className="text-[11px] font-bold text-slate-400 leading-relaxed uppercase tracking-tight">
                 Accepting this invitation grants you access to record vouchers, view reports and manage billing based on your assigned credentials.
              </p>
           </div>
        </CardContent>

        <CardFooter className="flex flex-col space-y-6 pt-6 pb-16 px-10">
          <Button
            onClick={handleAccept}
            className="w-full h-16 text-lg font-black uppercase tracking-widest bg-blue-600 hover:bg-blue-700 shadow-[0_20px_50px_rgba(37,99,235,0.3)] rounded-[24px] group transition-all relative overflow-hidden"
            disabled={loading}
          >
            {loading ? "Initializing Workspace..." : (
              <div className="flex items-center gap-3">
                 Accept Invitation
                 <ArrowRight className="h-5 w-5 group-hover:translate-x-1.5 transition-all stroke-[3]" />
              </div>
            )}
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:animate-[shimmer_2s_infinite] pointer-events-none" />
          </Button>

          <p className="text-[10px] font-black text-slate-400 text-center uppercase tracking-widest italic opacity-60">
             This invitation secure link expires in 48 hours
          </p>
        </CardFooter>

        <div className="bg-slate-900 py-5 px-10 text-center flex items-center justify-center gap-3">
           <div className="h-1 w-1 rounded-full bg-blue-400 animate-ping" />
           <p className="text-[9px] font-black text-blue-400 uppercase tracking-[0.3em]">Secure Provisioning Node-12</p>
        </div>
      </Card>
    </div>
  );
}
