import React, { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { API_BASE_URL } from '../config'
import { getToken } from '../lib/authStorage'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'

export default function ClientDetailPage() {
  const { id } = useParams()
  const [client, setClient] = useState(null)
  const [tx, setTx] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let alive = true
    const run = async () => {
      setLoading(true); setError('')
      try {
        // profile
        const res = await fetch(`${API_BASE_URL}/api/admin/clients/${id}`, {
          headers: { Authorization: `Bearer ${getToken()}` }
        })
        if (!res.ok) throw new Error(`Client fetch failed: ${res.status}`)
        const data = await res.json()
        if (!alive) return
        setClient(data.client || data)
        // transactions (best-effort)
        try {
          const r2 = await fetch(`${API_BASE_URL}/api/admin/clients/${id}/transactions`, {
            headers: { Authorization: `Bearer ${getToken()}` }
          })
          if (r2.ok) {
            const d2 = await r2.json()
            setTx(d2.transactions || d2.items || [])
          }
        } catch {}
      } catch (e) {
        if (alive) setError(e.message || 'Failed to load client')
      } finally {
        if (alive) setLoading(false)
      }
    }
    run()
    return () => { alive = false }
  }, [id])

  if (loading) return <div className="p-6">Loading…</div>
  if (error)   return <div className="p-6 text-rose-600">{error}</div>
  if (!client) return <div className="p-6">Client not found.</div>

  const balance = client.balance ?? client.aum ?? 0
  const kyc = client.kyc_status ?? client.status ?? '—'

  return (
    <div className="px-4 md:px-8 py-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold tracking-tight">Client: {client.name || client.email || client.id}</h1>
        <div className="flex gap-2">
          <Button asChild variant="outline" className="rounded-xl"><Link to="/clients">Back to Clients</Link></Button>
          <Button className="rounded-xl">Message</Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Card className="rounded-2xl lg:col-span-2">
          <CardHeader><CardTitle>Profile</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            <div><span className="text-slate-500 text-sm">ID:</span> <span className="font-medium">{client.id ?? '—'}</span></div>
            <div><span className="text-slate-500 text-sm">Name:</span> <span className="font-medium">{client.name ?? '—'}</span></div>
            <div><span className="text-slate-500 text-sm">Email:</span> <span className="font-medium">{client.email ?? '—'}</span></div>
            <div><span className="text-slate-500 text-sm">Status:</span> <span className="font-medium">{kyc}</span></div>
          </CardContent>
        </Card>

        <Card className="rounded-2xl">
          <CardHeader><CardTitle>Balances</CardTitle></CardHeader>
          <CardContent>
            <div className="text-3xl font-semibold">${Number(balance).toLocaleString()}</div>
            <div className="text-xs text-slate-500 mt-1">Total balance / AUM</div>
          </CardContent>
        </Card>
      </div>

      <Card className="rounded-2xl">
        <CardHeader><CardTitle>Recent Transactions</CardTitle></CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Date</TableHead>
                <TableHead>Type</TableHead>
                <TableHead className="text-right">Amount</TableHead>
                <TableHead>Note</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {tx.length === 0 ? (
                <TableRow><TableCell colSpan={4}>No transactions</TableCell></TableRow>
              ) : tx.map((t, i) => (
                <TableRow key={t.id ?? i}>
                  <TableCell>{t.date ?? t.created_at ?? '—'}</TableCell>
                  <TableCell>{t.type ?? '—'}</TableCell>
                  <TableCell className="text-right">${Number(t.amount || 0).toLocaleString()}</TableCell>
                  <TableCell>{t.note ?? '—'}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
