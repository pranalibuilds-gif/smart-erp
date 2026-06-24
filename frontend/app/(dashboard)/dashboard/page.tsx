"use client";

import { useEffect, useState, useMemo } from "react";
import { useAuthStore } from "@/stores/auth-store";
import { useCompanyStore } from "@/stores/company-store";
import apiClient from "@/lib/api-client";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button, buttonVariants } from "@/components/ui/button";
import {
  TrendingUp,
  TrendingDown,
  ArrowUpRight,
  ArrowDownRight,
  Receipt,
  Users,
  Package,
  BarChart3,
  Wallet,
  Landmark,
  FileText,
  Clock,
  Plus,
  Target,
  ArrowRightLeft,
  ChevronRight
} from "lucide-react";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  Legend
} from 'recharts';

const SALES_DATA = [
  { name: 'Apr', sales: 4000, expenses: 2400 },
  { name: 'May', sales: 3000, expenses: 1398 },
  { name: 'Jun', sales: 2000, expenses: 9800 },
  { name: 'Jul', sales: 2780, expenses: 3908 },
  { name: 'Aug', sales: 1890, expenses: 4800 },
  { name: 'Sep', sales: 2390, expenses: 3800 },
  { name: 'Oct', sales: 3490, expenses: 4300 },
  { name: 'Nov', sales: 4000, expenses: 2000 },
  { name: 'Dec', sales: 5000, expenses: 2100 },
  { name: 'Jan', sales: 4500, expenses: 2200 },
  { name: 'Feb', sales: 3800, expenses: 1900 },
  { name: 'Mar', sales: 5500, expenses: 2500 },
];

const EXPENSE_DATA = [
  { name: 'Direct Cost', value: 400 },
  { name: 'Operational', value: 300 },
  { name: 'Marketing', value: 200 },
  { name: 'Infrastructure', value: 278 },
];

const COLORS = ['#2563eb', '#6366f1', '#a855f7', '#ec4899'];

export default function DashboardPage() {
  const { activeCompany, activeFY } = useCompanyStore();
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [chartView, setChartView] = useState<"monthly" | "quarterly">("monthly");

  useEffect(() => {
    if (activeCompany && activeFY) {
      setLoading(true);
      apiClient.get("/api/v1/reports/dashboard-metrics")
        .then(res => setMetrics(res.data.data))
        .catch(console.error)
        .finally(() => setLoading(false));
    }
  }, [activeCompany, activeFY]);

  const quarterlyData = useMemo(() => {
    const quarters = [
      { name: 'Q1 (Apr-Jun)', sales: 0, expenses: 0 },
      { name: 'Q2 (Jul-Sep)', sales: 0, expenses: 0 },
      { name: 'Q3 (Oct-Dec)', sales: 0, expenses: 0 },
      { name: 'Q4 (Jan-Mar)', sales: 0, expenses: 0 },
    ];

    SALES_DATA.forEach((item, index) => {
      if (index < 3) { // Apr, May, Jun
        quarters[0].sales += item.sales;
        quarters[0].expenses += item.expenses;
      } else if (index < 6) { // Jul, Aug, Sep
        quarters[1].sales += item.sales;
        quarters[1].expenses += item.expenses;
      } else if (index < 9) { // Oct, Nov, Dec
        quarters[2].sales += item.sales;
        quarters[2].expenses += item.expenses;
      } else { // Jan, Feb, Mar
        quarters[3].sales += item.sales;
        quarters[3].expenses += item.expenses;
      }
    });
    return quarters;
  }, []);

  const displayData = chartView === "monthly" ? SALES_DATA : quarterlyData;

  const KpiCard = ({ title, value, icon: Icon, color, trend, sub }: any) => (
    <Card className="overflow-hidden border-none shadow-sm bg-white ring-1 ring-slate-200 transition-all duration-300 hover:shadow-xl hover:-translate-y-1">
      <CardContent className="p-7">
        <div className="flex justify-between items-start">
          <div className="space-y-3">
            <p className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">{title}</p>
            <h3 className="text-2xl font-black text-slate-900 tracking-tight">₹{value.toLocaleString('en-IN', { minimumFractionDigits: 0 })}</h3>
            <div className="flex items-center gap-2">
               <div className={cn("flex items-center gap-0.5 px-1.5 py-0.5 rounded-full text-[10px] font-black", trend > 0 ? "bg-emerald-50 text-emerald-600" : "bg-rose-50 text-rose-600")}>
                  {trend > 0 ? <ArrowUpRight className="h-2.5 w-2.5" /> : <ArrowDownRight className="h-2.5 w-2.5" />}
                  {Math.abs(trend)}%
               </div>
               <span className="text-[10px] font-bold text-slate-400 uppercase">vs last month</span>
            </div>
          </div>
          <div className={cn("p-3 rounded-2xl shadow-lg", color)}>
            <Icon className="h-6 w-6 text-white" />
          </div>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="p-8 max-w-[1700px] mx-auto space-y-10 pb-24 animate-in fade-in duration-700">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
        <div>
          <div className="flex items-center gap-2 mb-2">
             <div className="w-2 h-2 rounded-full bg-blue-600 shadow-[0_0_10px_#2563eb]" />
             <span className="text-[10px] font-black text-blue-600 uppercase tracking-widest">Main Dashboard</span>
          </div>
          <h1 className="text-4xl font-black tracking-tighter text-slate-900 uppercase">Executive Overview</h1>
          <p className="text-slate-500 mt-1 font-medium">Monitoring real-time performance for <span className="text-slate-900 font-bold underline decoration-blue-500/30 decoration-4 underline-offset-4">{activeCompany?.name}</span></p>
        </div>
        <div className="flex gap-4">
          <Link href="/reports/trial-balance" className={cn(buttonVariants({ variant: "outline" }), "bg-white border-slate-200 h-12 px-6 font-bold shadow-sm")}>
            <BarChart3 className="mr-2 h-4 w-4" /> Comprehensive Reports
          </Link>
          <Link href="/invoices/new" className={cn(buttonVariants(), "bg-blue-600 hover:bg-blue-700 h-12 px-8 font-black shadow-lg shadow-blue-600/30 tracking-tight uppercase")}>
            <Plus className="mr-2 h-4 w-4" /> Record Entry
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-7">
        <KpiCard title="Net Receivables" value={metrics?.total_receivables || 845000} icon={Users} color="bg-blue-600" trend={12.5} />
        <KpiCard title="Net Payables" value={metrics?.total_payables || 1275200} icon={Wallet} color="bg-rose-500" trend={-4.2} />
        <KpiCard title="Operational Revenue" value={metrics?.total_sales || 2580000} icon={TrendingUp} color="bg-indigo-600" trend={18.4} />
        <KpiCard title="Inventory Value" value={metrics?.inventory_value || 5876000} icon={Package} color="bg-orange-500" trend={8.1} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <Card className="lg:col-span-2 border-none shadow-sm ring-1 ring-slate-200 overflow-hidden">
          <CardHeader className="flex flex-row items-center justify-between pb-10 px-8 pt-8">
            <div>
              <CardTitle className="text-xl font-black tracking-tight text-slate-900">Revenue Distribution Trend</CardTitle>
              <CardDescription className="font-medium">Sales vs Expenditure analysis (Current FY)</CardDescription>
            </div>
            <div className="flex items-center gap-3 bg-slate-100 p-1 rounded-xl border border-slate-200 shadow-inner">
               <button
                 onClick={() => setChartView("monthly")}
                 className={cn(
                   "px-4 py-1.5 text-[10px] font-black uppercase tracking-widest rounded-lg transition-all",
                   chartView === "monthly" ? "bg-white text-blue-600 shadow-sm" : "text-slate-500 hover:text-slate-900"
                 )}
               >
                 Monthly
               </button>
               <button
                 onClick={() => setChartView("quarterly")}
                 className={cn(
                   "px-4 py-1.5 text-[10px] font-black uppercase tracking-widest rounded-lg transition-all",
                   chartView === "quarterly" ? "bg-white text-blue-600 shadow-sm" : "text-slate-500 hover:text-slate-900"
                 )}
               >
                 Quarterly
               </button>
            </div>
          </CardHeader>
          <CardContent className="h-[400px] px-4 pb-8">
             <ResponsiveContainer width="100%" height="100%">
               <AreaChart data={displayData}>
                 <defs>
                   <linearGradient id="colorSales" x1="0" y1="0" x2="0" y2="1">
                     <stop offset="5%" stopColor="#2563eb" stopOpacity={0.15}/>
                     <stop offset="95%" stopColor="#2563eb" stopOpacity={0}/>
                   </linearGradient>
                 </defs>
                 <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                 <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fontSize: 10, fill: '#94a3b8', fontWeight: 800}} dy={15} />
                 <YAxis axisLine={false} tickLine={false} tick={{fontSize: 10, fill: '#94a3b8', fontWeight: 800}} tickFormatter={(v) => `₹${v/1000}k`} />
                 <Tooltip
                   contentStyle={{borderRadius: '16px', border: 'none', boxShadow: '0 25px 50px -12px rgb(0 0 0 / 0.1)', padding: '15px'}}
                   itemStyle={{fontWeight: '900', textTransform: 'uppercase', fontSize: '10px'}}
                 />
                 <Area type="monotone" dataKey="sales" stroke="#2563eb" strokeWidth={4} fillOpacity={1} fill="url(#colorSales)" dot={{r: 4, fill: '#2563eb', strokeWidth: 2, stroke: '#fff'}} activeDot={{r: 7, shadow: '0 0 10px #2563eb'}} />
               </AreaChart>
             </ResponsiveContainer>
          </CardContent>
        </Card>

        <div className="space-y-8">
          <Card className="border-none shadow-sm ring-1 ring-slate-200 overflow-hidden">
            <CardHeader className="px-8 pt-8">
              <CardTitle className="text-xl font-black tracking-tight text-slate-900">Expense Allocation</CardTitle>
              <CardDescription className="font-medium">Top 4 spending categories</CardDescription>
            </CardHeader>
            <CardContent className="h-[300px] px-4">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={EXPENSE_DATA}
                    innerRadius={70}
                    outerRadius={95}
                    paddingAngle={8}
                    dataKey="value"
                    stroke="none"
                  >
                    {EXPENSE_DATA.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend verticalAlign="bottom" align="center" iconType="circle" wrapperStyle={{fontSize: '10px', fontWeight: '900', textTransform: 'uppercase', letterSpacing: '0.1em', paddingTop: '20px'}} />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card className="border-none shadow-sm ring-1 ring-slate-900 bg-[#0f172a] text-white overflow-hidden relative group">
            <div className="absolute top-0 right-0 w-32 h-32 bg-blue-600/10 rounded-full -mr-16 -mt-16 blur-3xl group-hover:bg-blue-600/20 transition-all duration-700" />
            <CardHeader className="pb-4 border-b border-white/5 relative">
              <CardTitle className="text-xs font-black uppercase tracking-[0.3em] text-blue-400">Inventory Insights</CardTitle>
            </CardHeader>
            <CardContent className="pt-8 space-y-7 relative">
               <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <p className="text-[10px] font-black text-white/40 uppercase tracking-widest">Aggregate Valuation</p>
                    <p className="text-3xl font-black tracking-tighter">₹5,876,000</p>
                  </div>
                  <div className="bg-blue-600 p-3 rounded-2xl shadow-xl shadow-blue-600/20 ring-4 ring-blue-600/10">
                     <Target className="h-6 w-6 text-white" />
                  </div>
               </div>
               <div className="grid grid-cols-2 gap-4">
                  <div className="bg-white/5 p-4 rounded-2xl border border-white/5 transition-colors hover:bg-white/10">
                     <p className="text-[10px] font-black text-white/40 uppercase tracking-widest mb-1">Turnover</p>
                     <p className="text-xl font-black">2.35x</p>
                  </div>
                  <div className="bg-white/5 p-4 rounded-2xl border border-white/5 transition-colors hover:bg-white/10">
                     <p className="text-[10px] font-black text-white/40 uppercase tracking-widest mb-1">Util. Rate</p>
                     <p className="text-xl font-black text-emerald-400">94.2%</p>
                  </div>
               </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
         <Card className="border-none shadow-sm ring-1 ring-slate-200 lg:col-span-1 bg-slate-50/30 overflow-hidden">
            <CardHeader className="pb-4 px-7 pt-7">
               <CardTitle className="text-xs font-black uppercase tracking-[0.2em] flex items-center gap-3 text-slate-500">
                  <div className="w-1.5 h-1.5 rounded-full bg-blue-500" /> System Feed
               </CardTitle>
            </CardHeader>
            <CardContent className="px-7 space-y-6">
               {[1, 2, 3, 4].map(i => (
                 <div key={i} className="flex gap-4 pb-6 border-b border-slate-100 last:border-0 last:pb-0 group/feed cursor-pointer">
                    <div className="h-10 w-10 rounded-xl bg-white border border-slate-200 flex items-center justify-center text-xs font-black text-slate-400 group-hover/feed:border-blue-300 group-hover/feed:text-blue-600 transition-all shadow-sm shadow-slate-100">SA</div>
                    <div className="flex-1 min-w-0">
                       <p className="text-xs font-black text-slate-900 group-hover/feed:text-blue-600 transition-colors">Voucher #00{i*10} Posted</p>
                       <p className="text-[10px] text-slate-400 font-bold uppercase mt-0.5 tracking-tighter">15m ago • Accounts Module</p>
                    </div>
                 </div>
               ))}
               <Link href="/activity" className="flex items-center justify-between p-4 bg-white border border-slate-200 rounded-2xl hover:border-blue-500 transition-all group shadow-sm">
                  <span className="text-[10px] font-black uppercase tracking-widest text-slate-500 group-hover:text-blue-600">Full Audit History</span>
                  <ChevronRight className="h-4 w-4 text-slate-300 group-hover:text-blue-600 group-hover:translate-x-1 transition-all" />
               </Link>
            </CardContent>
         </Card>

         <Card className="border-none shadow-sm ring-1 ring-slate-200 lg:col-span-3 overflow-hidden">
            <CardHeader className="bg-slate-50/50 border-b flex flex-row items-center justify-between px-8 py-7">
               <div>
                  <CardTitle className="text-xl font-black tracking-tight text-slate-900 uppercase italic">Cash Flow Dynamics</CardTitle>
                  <CardDescription className="font-medium">Inbound receipts vs outbound settlement volume</CardDescription>
               </div>
               <div className="bg-blue-600/10 p-3 rounded-2xl">
                  <ArrowRightLeft className="h-5 w-5 text-blue-600" />
               </div>
            </CardHeader>
            <CardContent className="h-[280px] pt-10 px-6 pb-6">
               <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={displayData}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                    <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fontSize: 10, fontWeight: '800', fill: '#94a3b8'}} />
                    <YAxis axisLine={false} tickLine={false} tick={{fontSize: 10, fontWeight: '800', fill: '#94a3b8'}} />
                    <Tooltip cursor={{fill: '#f8fafc'}} contentStyle={{borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)'}} />
                    <Bar dataKey="sales" fill="#2563eb" radius={[6, 6, 0, 0]} barSize={32} shadow="0 10px 15px #2563eb" />
                  </BarChart>
               </ResponsiveContainer>
            </CardContent>
         </Card>
      </div>
    </div>
  );
}
