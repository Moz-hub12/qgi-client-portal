import React, { useEffect, useState } from 'react'
import { API_BASE_URL } from '../config'
import { getToken } from '../lib/authStorage'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import ShieldCheck from 'lucide-react/dist/esm/icons/shield-check'
import Search from 'lucide-react/dist/esm/icons/search'

export default function CompliancePage() {
  const [q, setQ] = useState('')
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    let alive = true
    const run = async () => {
      setLoading(true); setError('')
      try {
        const url = new URL(`${API_BASE_URL}/api/admin/compliance/flags`)
        if (q.trim()) url.searchParams.set('q', q.trim())
        const res = await fetch(url.toString(), { headers: { Authorization: `Bearer ${getToken()}` } })
        if (!res.ok) throw new Error(`Fetch failed: ${res.status}`)
        const data = await res.json()
        if (!alive) return
        setItems(data.items || data.flags || [])
      } catch (e) {
        if (alive) setError(e.message || 'Failed to load compliance data')
      } finally {
        if (alive) setLoading(false)
      }
    }
    run()
    return () => { alive = false }
  }, [q])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold tracking-tight flex items-center gap-2">
          <ShieldCheck className="h-6 w-6 text-amber-500" /> Compliance
        </h1>
        <div className="flex gap-2">
          <Button variant="outline" className="rounded-xl">Export</Button>
          <Button className="rounded-xl">New Review</Button>
        </div>
      </div>

      <Card className="rounded-2xl">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Flags & Reviews</CardTitle>
          <div className="relative">
            <Input value={q} onChange={(e)=>setQ(e.target.value)} placeholder="Search client, note, ref…" className="pl-9 rounded-xl" />
            <Search className="h-4 w-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          </div>
        </CardHeader>
        <CardContent>
          {error && <div className="text-sm text-rose-600 mb-3">{error}</div>}
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Ref</TableHead>
                <TableHead>Client</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Severity</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Updated</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow><TableCell colSpan={6}>Loading…</TableCell></TableRow>
              ) : items.length === 0 ? (
                <TableRow><TableCell colSpan={6}>No flags found</TableCell></TableRow>
              ) : items.map((r, i) => (
                <TableRow key={r.id ?? r.ref ?? i}>
                  <TableCell className="font-medium">{r.ref ?? r.id ?? '—'}</TableCell>
                  <TableCell>{r.client_name ?? r.client_id ?? '—'}</TableCell>
                  <TableCell>{r.type ?? '—'}</TableCell>
                  <TableCell>
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      r.severity === 'high' ? 'bg-rose-100 text-rose-700' :
                      r.severity === 'medium' ? 'bg-amber-100 text-amber-700' :
                      'bg-slate-100 text-slate-700'
                    }`}>{r.severity ?? '—'}</span>
                  </TableCell>
                  <TableCell>{r.status ?? 'Open'}</TableCell>
                  <TableCell>{r.updated_at ?? r.created_at ?? '—'}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
