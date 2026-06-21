"use client";

import { useEffect, useState } from "react";
import { getAuditLogs, AuditLog } from "@/features/audit/api/audit-api";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { format } from "date-fns";

export default function ActivityCenterPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAuditLogs({ limit: 50 })
      .then(setLogs)
      .finally(() => setLoading(false));
  }, []);

  const getActionColor = (action: string) => {
    switch (action) {
      case "CREATE": return "bg-blue-100 text-blue-700";
      case "POST": return "bg-green-100 text-green-700";
      case "CANCEL": return "bg-red-100 text-red-700";
      case "LOGIN": return "bg-purple-100 text-purple-700";
      default: return "bg-gray-100 text-gray-700";
    }
  };

  if (loading) return <div className="p-8">Loading logs...</div>;

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">Activity Center</h1>

      <div className="bg-white border rounded-lg overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Time</TableHead>
              <TableHead>User</TableHead>
              <TableHead>Entity</TableHead>
              <TableHead>Action</TableHead>
              <TableHead>Changes</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {logs.map((log) => (
              <TableRow key={log.id}>
                <td className="px-4 py-4 text-xs font-mono text-gray-500">
                  {format(new Date(log.created_at), "yyyy-MM-dd HH:mm:ss")}
                </td>
                <td className="px-4 py-4 font-medium">{log.user_full_name || "System"}</td>
                <td className="px-4 py-4 text-xs font-bold uppercase text-gray-500">{log.entity_type}</td>
                <td className="px-4 py-4">
                  <Badge className={getActionColor(log.action)} variant="outline">{log.action}</Badge>
                </td>
                <td className="px-4 py-4 text-xs max-w-md">
                   {log.new_values && (
                      <div className="bg-gray-50 p-2 rounded border truncate">
                         {JSON.stringify(log.new_values)}
                      </div>
                   )}
                </td>
              </TableRow>
            ))}
            {logs.length === 0 && (
              <TableRow>
                <TableCell colSpan={5} className="text-center py-12 text-gray-400">No activity recorded yet</TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
