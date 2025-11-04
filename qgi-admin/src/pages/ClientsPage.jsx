import React, { useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams, useNavigate } from 'react-router-dom'
import { apiFetch } from '../lib/apiFetch'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
// Optimized icon imports for tree-shaking
import ChevronLeft from 'lucide-react/dist/esm/icons/chevron-left'
import ChevronRight from 'lucide-react/dist/esm/icons/chevron-right'
import ChevronsLeft from 'lucide-react/dist/esm/icons/chevrons-left'
import ChevronsRight from 'lucide-react/dist/esm/icons/chevrons-right'
import Search from 'lucide-react/dist/esm/icons/search'

// --- Helpers ---------------------------------------------------------------
const PAGE_SIZES = [10, 25, 50, 100]

function safeNumber(n, fallback = 0) {
  const v = Number(n)
  return Number.isFinite(v) ? v : fallback
}

function normalizeClients(payload) {
  // Accept several shapes to be resilient to backend changes
  const items = payload?.clients ?? payload?.items ?? payload?.data ?? payload ?? []
  const total = payload?.total ?? payload?.count ?? items.length
  return {
    items: items.map((c) => ({
      id: c.id ?? c.client_id ?? c._id ?? '',
      name:
        c.name ??
        (([c.first_name, c.last_name].filter(Boolean).join(' ')) ||
        c.email ||
        '—'),
      email: c.email ?? '—',
      status: c.status ?? c.kyc_status ?? '—',
      balance: c.balance ?? c.aum ?? 0,
      created_at: c.created_at ?? c.createdAt ?? c.joined_at ?? null,
    })),
    total: safeNumber(total),
  }
}

// --- Component -------------------------------------------------------------
export default function ClientsPage() {
  const navigate = useNavigate()
  const [sp, setSp] = useSearchParams()

  // URL state (kept in query params for shareability)
  const [q, setQ] = useState(sp.get('q') || '')
  const [page, setPage] = useState(safeNumber(sp.get('page'), 1))
  const [limit, setLimit] = useState(safeNumber(sp.get('limit'), 25))
  const [sortBy, setSortBy] = useState(sp.get('sortBy') || 'created_at')
  const [sortDir, setSortDir] = useState(sp.get('sortDir') || 'desc') // 'asc' | 'desc'

  // Data state
  const [rows, setRows] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Keep URL in sync when these change
  useEffect(() => {
    const params = new URLSearchParams()
    if (q) params.set('q', q)
    if (page !== 1) params.set('page', String(page))
    if (limit !== 25) params.set('limit', String(limit))
    if (sortBy !== 'created_at') params.set('sortBy', sortBy)
    if (sortDir !== 'desc') params.set('sortDir', sortDir)
    setSp(params, { replace: true })
  }, [q, page, limit, sortBy, sortDir, setSp])

  // Debounce search
  const [debouncedQ, setDebouncedQ] = useState(q)
  useEffect(() => {
    const t = setTimeout(() => setDebouncedQ(q.trim()), 350)
    return () => clearTimeout(t)
  }, [q])

  // Fetch clients from API
  useEffect(() => {
    let alive = true
    const run = async () => {
      setLoading(true)
      setError('')
      try {
        const params = new URLSearchParams()
        if (debouncedQ) params.set('q', debouncedQ)
        params.set('page', String(page))
        params.set('limit', String(limit))
        params.set('sortBy', sortBy)
        params.set('sortDir', sortDir)

        const res = await apiFetch(`/api/admin/clients?${params.toString()}`, { method: 'GET' })
        if (!res.ok) throw new Error(`Fetch failed: ${res.status}`)
        const payload = await res.json()
        if (!alive) return

        const { items, total } = normalizeClients(payload)
        setRows(items)
        setTotal(total)

        // If current page is now out of range (e.g., filters reduced results), bounce to last page
        const lastPage = Math.max(1, Math.ceil(total / limit))
        if (page > lastPage) setPage(lastPage)
      } catch (e) {
        if (alive) setError(e.message || 'Failed to load clients')
      } finally {
        if (alive) setLoading(false)
      }
    }
    run()
    return () => { alive = false }
  }, [debouncedQ, page, limit, sortBy, sortDir])

  const lastPage = useMemo(() => Math.max(1, Math.ceil(total / limit)), [total, limit])

  // Sorting (client-side hook that maps to server-side sort fields)
  const toggleSort = (field) => {
    if (sortBy !== field) {
      setSortBy(field)
      setSortDir('asc')
    } else {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'))
    }
    setPage(1)
  }

  // Export CSV (adjust path if your backend differs)
  const handleExport = async () => {
    try {
      const params = new URLSearchParams()
      if (debouncedQ) params.set('q', debouncedQ)
      params.set('sortBy', sortBy)
      params.set('sortDir', sortDir)
      // Optional: include full dataset by using a high limit or a dedicated export endpoint
      // params.set('limit', '10000')

      // If you have a dedicated export route, prefer that:
      // const res = await apiFetch(`/api/admin/clients/export?${params.toString()}`, { method: 'GET' })
      const res = await apiFetch(`/api/admin/clients?${params.toString()}`, { method: 'GET' })
      if (!res.ok) throw new Error('Export failed')
      const payload = await res.json()
      const { items } = normalizeClients(payload)

      // Build CSV in-browser
      const headers = ['id', 'name', 'email', 'status', 'balance', 'created_at']
      const lines = [
        headers.join(','),
        ...items.map((r) =>
          [
            JSON.stringify(r.id ?? ''),        // wrap in JSON.stringify to safely quote
            JSON.stringify(r.name ?? ''),
            JSON.stringify(r.email ?? ''),
            JSON.stringify(r.status ?? ''),
            String(r.balance ?? 0),
            JSON.stringify(r.created_at ?? ''),
          ].join(',')
        ),
      ]
      const blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8;' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `clients_${new Date().toISOString().slice(0,19).replace(/[:T]/g,'-')}.csv`
      a.click()
      URL.revokeObjectURL(url)
    } catch (e) {
      if (import.meta.env.DEV) {
        console.error(e)
      }
      alert('Export failed')
    }
  }

  return (
    <div className="space-y-6">
      {/* Heading */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold tracking-tight">Clients</h1>
        <div className="flex gap-2">
          <Button variant="outline" className="rounded-xl" onClick={handleExport}>Export</Button>
        </div>
      </div>

      {/* Filters */}
      <Card className="rounded-2xl">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>All Clients</CardTitle>
          <div className="flex gap-2 items-center">
            <div className="relative">
              <Input
                value={q}
                onChange={(e) => { setQ(e.target.value); setPage(1) }}
                placeholder="Search name, email, ID…"
                className="pl-9 rounded-xl w-[260px]"
              />
              <Search className="h-4 w-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
            </div>
            <Select
              value={String(limit)}
              onValueChange={(v) => { setLimit(Number(v)); setPage(1) }}
            >
              <SelectTrigger className="w-28 rounded-xl">
                <SelectValue placeholder="Rows / page" />
              </SelectTrigger>
              <SelectContent>
                {PAGE_SIZES.map((s) => (
                  <SelectItem key={s} value={String(s)}>{s} / page</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardHeader>

        <CardContent>
          {error && (
            <div className="text-sm text-rose-600 bg-rose-50 dark:bg-rose-950/30 p-3 rounded-xl mb-3">
              {error}
            </div>
          )}

          <Table>
            <TableHeader>
              <TableRow>
                <TableHead onClick={() => toggleSort('id')} className="cursor-pointer">ID {sortBy === 'id' ? (sortDir === 'asc' ? '↑' : '↓') : ''}</TableHead>
                <TableHead onClick={() => toggleSort('name')} className="cursor-pointer">Name {sortBy === 'name' ? (sortDir === 'asc' ? '↑' : '↓') : ''}</TableHead>
                <TableHead onClick={() => toggleSort('email')} className="cursor-pointer">Email {sortBy === 'email' ? (sortDir === 'asc' ? '↑' : '↓') : ''}</TableHead>
                <TableHead onClick={() => toggleSort('balance')} className="text-right cursor-pointer">Balance {sortBy === 'balance' ? (sortDir === 'asc' ? '↑' : '↓') : ''}</TableHead>
                <TableHead onClick={() => toggleSort('status')} className="cursor-pointer">Status {sortBy === 'status' ? (sortDir === 'asc' ? '↑' : '↓') : ''}</TableHead>
                <TableHead onClick={() => toggleSort('created_at')} className="cursor-pointer">Created {sortBy === 'created_at' ? (sortDir === 'asc' ? '↑' : '↓') : ''}</TableHead>
                <TableHead />
              </TableRow>
            </TableHeader>

            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={7}>
                    <div className="py-8 flex items-center justify-center">
                      <div className="animate-spin rounded-full h-6 w-6 border-2 border-muted-foreground border-t-transparent" />
                    </div>
                  </TableCell>
                </TableRow>
              ) : rows.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center text-slate-500 py-8">
                    No clients found
                  </TableCell>
                </TableRow>
              ) : (
                rows.map((r) => (
                  <TableRow key={r.id}>
                    <TableCell className="font-medium">{r.id}</TableCell>
                    <TableCell>{r.name}</TableCell>
                    <TableCell>{r.email}</TableCell>
                    <TableCell className="text-right">${Number(r.balance || 0).toLocaleString()}</TableCell>
                    <TableCell>
                      <span
                        className={`px-2 py-1 text-xs rounded-full ${
                          r.status === 'Active'
                            ? 'bg-emerald-100 text-emerald-700'
                            : r.status === 'Flagged'
                            ? 'bg-rose-100 text-rose-700'
                            : 'bg-amber-100 text-amber-700'
                        }`}
                      >
                        {r.status}
                      </span>
                    </TableCell>
                    <TableCell>{r.created_at ? String(r.created_at).slice(0,10) : '—'}</TableCell>
                    <TableCell className="text-right">
                      <Button asChild size="sm" className="rounded-xl">
                        <Link to={`/clients/${encodeURIComponent(r.id)}`}>Open</Link>
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>

          {/* Pagination */}
          <div className="flex items-center justify-between mt-4">
            <div className="text-sm text-slate-600">
              {rows.length ? (
                <>
                  Showing <strong>{(page - 1) * limit + 1}</strong>–
                  <strong>{Math.min(page * limit, total)}</strong> of <strong>{total}</strong>
                </>
              ) : (
                <>Showing 0 of 0</>
              )}
            </div>
            <div className="flex items-center gap-1">
              <Button
                variant="outline"
                size="icon"
                className="rounded-xl"
                onClick={() => setPage(1)}
                disabled={page <= 1}
                title="First"
              >
                <ChevronsLeft className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                size="icon"
                className="rounded-xl"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
                title="Prev"
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <div className="px-3 text-sm tabular-nums">
                Page <strong>{page}</strong> / {lastPage}
              </div>
              <Button
                variant="outline"
                size="icon"
                className="rounded-xl"
                onClick={() => setPage((p) => Math.min(lastPage, p + 1))}
                disabled={page >= lastPage}
                title="Next"
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                size="icon"
                className="rounded-xl"
                onClick={() => setPage(lastPage)}
                disabled={page >= lastPage}
                title="Last"
              >
                <ChevronsRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

