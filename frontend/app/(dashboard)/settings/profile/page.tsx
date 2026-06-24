"use client";

import { useAuthStore } from "@/stores/auth-store";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { User, Mail, Shield, Save, Key, Camera } from "lucide-react";
import { useForm } from "react-hook-form";

export default function UserProfilePage() {
  const { user } = useAuthStore();

  const { register, handleSubmit } = useForm({
    defaultValues: user || {}
  });

  const onSubmit = (data: any) => {
    alert("Profile update logic would integrate here");
  };

  return (
    <div className="p-10 max-w-4xl mx-auto space-y-10 pb-32 animate-in fade-in duration-700">
      <div className="flex justify-between items-end border-b border-slate-200 pb-10">
        <div className="flex items-center gap-6">
          <div className="relative group">
             <div className="bg-blue-600 p-4 rounded-[24px] shadow-2xl shadow-blue-500/40 text-white ring-8 ring-blue-50">
               <User className="h-8 w-8" />
             </div>
             <button className="absolute -bottom-2 -right-2 bg-white p-2 rounded-xl shadow-lg border border-slate-100 text-blue-600 opacity-0 group-hover:opacity-100 transition-opacity">
                <Camera className="h-4 w-4" />
             </button>
          </div>
          <div>
            <h1 className="text-4xl font-black tracking-tighter text-slate-900 uppercase italic">Personal Identity</h1>
            <p className="text-slate-400 font-bold uppercase tracking-widest mt-1 italic">Manage your portal access and security credentials</p>
          </div>
        </div>
        <Button
          onClick={handleSubmit(onSubmit)}
          className="bg-blue-600 hover:bg-blue-700 h-14 px-10 rounded-2xl font-black uppercase tracking-widest shadow-2xl shadow-blue-500/40 transition-all active:scale-95"
        >
          <Save className="mr-2 h-5 w-5" /> Commit Updates
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
         <Card className="border-none shadow-sm ring-1 ring-slate-200 rounded-[32px] overflow-hidden">
            <CardHeader className="bg-slate-50/50 border-b px-8 py-6">
               <CardTitle className="text-sm font-black uppercase tracking-[0.2em] flex items-center gap-3">
                  <Shield className="h-4 w-4 text-blue-600" /> Account Profile
               </CardTitle>
            </CardHeader>
            <CardContent className="p-8 space-y-6">
               <div className="space-y-2">
                  <Label className="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-1">Full Legal Name</Label>
                  <Input className="h-12 rounded-xl border-slate-200 font-bold" {...register("full_name")} />
               </div>
               <div className="space-y-2">
                  <Label className="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-1">Primary Email Access</Label>
                  <div className="relative">
                    <Mail className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-300" />
                    <Input className="h-12 pl-12 rounded-xl border-slate-200 font-bold bg-slate-50" {...register("email")} disabled />
                  </div>
               </div>
            </CardContent>
         </Card>

         <Card className="border-none shadow-sm ring-1 ring-slate-200 rounded-[32px] overflow-hidden">
            <CardHeader className="bg-slate-50/50 border-b px-8 py-6">
               <CardTitle className="text-sm font-black uppercase tracking-[0.2em] flex items-center gap-3">
                  <Key className="h-4 w-4 text-amber-500" /> Security Protocol
               </CardTitle>
            </CardHeader>
            <CardContent className="p-8 space-y-6 text-center">
               <div className="bg-amber-50 p-6 rounded-2xl border border-amber-100 mb-4">
                  <p className="text-xs font-bold text-amber-700 uppercase tracking-tight">Multi-Factor Authentication</p>
                  <p className="text-[10px] text-amber-600 mt-1 uppercase font-black">Deactivated</p>
               </div>
               <Button variant="outline" className="w-full h-12 rounded-xl border-slate-200 font-bold uppercase tracking-widest text-xs">
                  Change Master Password
               </Button>
               <Button variant="ghost" className="w-full h-12 rounded-xl text-slate-400 font-bold uppercase tracking-widest text-xs">
                  Review Access Logs
               </Button>
            </CardContent>
         </Card>
      </div>
    </div>
  );
}
