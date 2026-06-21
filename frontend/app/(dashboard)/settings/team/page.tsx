"use client";

import { useEffect, useState } from "react";
import apiClient from "@/lib/api-client";
import { useCompanyStore } from "@/stores/company-store";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Plus, UserPlus, Mail, Shield, Clock } from "lucide-react";
import { formatDistanceToNow } from "date-fns";

export default function TeamManagementPage() {
  const { currentCompany } = useCompanyStore();
  const [members, setMembers] = useState<any[]>([]);
  const [invites, setInvites] = useState<any[]>([]);
  const [roles, setRoles] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showInvite, setShowInvite] = useState(false);
  const [inviteData, setInviteData] = useState({ email: "", role_id: "" });

  const fetchData = async () => {
    if (!currentCompany) return;
    setLoading(true);
    try {
      const [membersRes, invitesRes, rolesRes] = await Promise.all([
        apiClient.get(`/api/v1/companies/${currentCompany.id}/members`),
        apiClient.get(`/api/v1/companies/${currentCompany.id}/invitations`),
        apiClient.get("/api/v1/auth/roles")
      ]);
      setMembers(membersRes.data.data);
      setInvites(invitesRes.data.data);
      setRoles(rolesRes.data.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [currentCompany]);

  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await apiClient.post(`/api/v1/companies/${currentCompany?.id}/invite`, inviteData);
      alert(`Invitation created! Token: ${res.data.data.token}`); // In real app, token is emailed
      setShowInvite(false);
      setInviteData({ email: "", role_id: "" });
      fetchData();
    } catch (err: any) {
      alert(err.response?.data?.detail || "Failed to invite");
    }
  };

  if (!currentCompany) return <div className="p-8">Please select a company first</div>;

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Team Management</h1>
        <Button onClick={() => setShowInvite(true)}><UserPlus className="mr-2 h-4 w-4" /> Invite Member</Button>
      </div>

      {showInvite && (
        <Card className="mb-8 border-blue-200 bg-blue-50/50">
          <CardHeader><CardTitle className="text-lg">Invite New Member</CardTitle></CardHeader>
          <CardContent>
            <form onSubmit={handleInvite} className="flex flex-col md:flex-row gap-4 items-end">
              <div className="flex-1 space-y-2">
                <label className="text-sm font-medium">Email Address</label>
                <input
                  type="email"
                  required
                  className="w-full h-9 rounded-md border px-3 text-sm bg-white"
                  value={inviteData.email}
                  onChange={e => setInviteData({...inviteData, email: e.target.value})}
                />
              </div>
              <div className="flex-1 space-y-2">
                <label className="text-sm font-medium">Role</label>
                <select
                  required
                  className="w-full h-9 rounded-md border px-3 text-sm bg-white"
                  value={inviteData.role_id}
                  onChange={e => setInviteData({...inviteData, role_id: e.target.value})}
                >
                  <option value="">Select Role</option>
                  {roles.map(r => <option key={r.id} value={r.id}>{r.name}</option>)}
                </select>
              </div>
              <div className="flex gap-2">
                <Button type="button" variant="ghost" onClick={() => setShowInvite(false)}>Cancel</Button>
                <Button type="submit">Send Invitation</Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      <div className="space-y-8">
        <Card>
          <CardHeader><CardTitle>Members</CardTitle></CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>User</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Last Active</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {members.map((m) => (
                  <TableRow key={m.user_id}>
                    <TableCell>
                      <div className="flex flex-col">
                        <span className="font-bold flex items-center gap-2">
                          {m.full_name} {m.is_owner && <Badge variant="outline" className="text-[10px] text-blue-600 border-blue-200">OWNER</Badge>}
                        </span>
                        <span className="text-xs text-gray-500">{m.email}</span>
                      </div>
                    </TableCell>
                    <TableCell><Badge variant="secondary">{m.role_name}</Badge></TableCell>
                    <TableCell className="text-xs text-gray-500">
                      {m.last_active_at ? formatDistanceToNow(new Date(m.last_active_at), { addSuffix: true }) : "Never"}
                    </TableCell>
                    <TableCell className="text-right">
                       {!m.is_owner && <Button variant="ghost" size="sm" className="text-red-500 hover:text-red-700">Remove</Button>}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {invites.length > 0 && (
          <Card>
            <CardHeader><CardTitle>Pending Invitations</CardTitle></CardHeader>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Email</TableHead>
                    <TableHead>Role</TableHead>
                    <TableHead>Invited By</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {invites.map((i) => (
                    <TableRow key={i.id}>
                      <TableCell className="font-medium">{i.email}</TableCell>
                      <TableCell>{i.role_name}</TableCell>
                      <TableCell className="text-sm">{i.invited_by_name}</TableCell>
                      <TableCell><Badge variant="outline">{i.status}</Badge></TableCell>
                      <TableCell className="text-right">
                        <Button variant="ghost" size="sm" className="text-red-500">Revoke</Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
