import { HealthCheck } from "@/features/health/HealthCheck";

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-4">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl text-slate-900">
          SmartERP
        </h1>
        <p className="text-slate-500 mt-2">
          Modular Enterprise Resource Planning System
        </p>
      </div>

      <HealthCheck />

      <div className="mt-8 text-sm text-slate-400">
        Phase 0B — Frontend Foundation
      </div>
    </main>
  );
}
