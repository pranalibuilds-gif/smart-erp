"use client";

import { useEffect, useState } from "react";
import apiClient from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Activity, CheckCircle2, XCircle } from "lucide-react";

export const HealthCheck = () => {
  const [status, setStatus] = useState<"loading" | "healthy" | "error">("loading");
  const [error, setError] = useState<string | null>(null);

  const checkHealth = async () => {
    setStatus("loading");
    setError(null);
    try {
      const response = await apiClient.get("/health");
      if (response.data.success) {
        setStatus("healthy");
      } else {
        setStatus("error");
        setError("API returned success: false");
      }
    } catch (err: any) {
      setStatus("error");
      setError(err.message);
    }
  };

  useEffect(() => {
    checkHealth();
  }, []);

  return (
    <div className="p-6 border rounded-lg shadow-sm bg-card text-card-foreground max-w-md mx-auto mt-10">
      <div className="flex items-center gap-4 mb-4">
        <Activity className="w-6 h-6 text-primary" />
        <h2 className="text-xl font-bold">System Health Check</h2>
      </div>

      <div className="flex items-center gap-2 mb-6">
        <span className="text-sm font-medium">Backend Status:</span>
        {status === "loading" && <span className="text-muted-foreground animate-pulse">Checking...</span>}
        {status === "healthy" && (
          <div className="flex items-center gap-1 text-green-600">
            <CheckCircle2 className="w-4 h-4" />
            <span className="font-bold">HEALTHY</span>
          </div>
        )}
        {status === "error" && (
          <div className="flex items-center gap-1 text-destructive">
            <XCircle className="w-4 h-4" />
            <span className="font-bold">UNREACHABLE</span>
          </div>
        )}
      </div>

      {error && (
        <div className="p-3 mb-6 text-sm bg-destructive/10 text-destructive rounded border border-destructive/20">
          {error}
        </div>
      )}

      <Button
        onClick={checkHealth}
        disabled={status === "loading"}
        className="w-full"
      >
        Retry Connection
      </Button>
    </div>
  );
};
