import React, { useEffect, useState } from 'react'
import { API_BASE_URL } from '../config'
import { getToken } from '../lib/authStorage'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { ResponsiveContainer, AreaChart, Area, CartesianGrid, XAxis, YAxis, Tooltip, BarChart, Bar } from 'recharts'
import BarChart3 from 'lucide-react/dist/esm/icons/bar-chart-3'

export default function ReportsPage() {
  const [equity, setEquity] = useState([])
  const [byInstrument, setByInstrument] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let alive = true
    const run = async () => {
      setLoading(true)
      try {
        // best-effort endpoints (adapt to your API)
        const [r1, r2] = await Promise.all([
          fetch(`${API_BASE_URL}/api/admin/reports/equity`,      { headers: { Authorization: `Bearer ${getToken()}` } }),
          fetch(`${API_BASE_URL}/api/admin/reports/instruments`, { headers: { Authorization: `Bearer ${getToken()}` } }),
        ])
        if (r1.ok) { const d1 = await r1.json(); if (alive) setEquity(d1.data || d1.equity || []) }
        if (r2.ok) { const d2 = await r2.json(); if (alive) setByInstrument(d2.data || d2.items || []) }
      } finally {
        if (alive) setLoading(false)
      }
    }
    run()
    return () => { alive = false }
  }, [])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold tracking-tight flex items-center gap-2">
          <BarChart3 className="h-6 w-6 text-amber-500" /> Reports
        </h1>
        <div className="flex gap-2">
          <Button variant="outline" className="rounded-xl">Export CSV</Button>
          <Button className="rounded-xl">Download PDF</Button>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        <Card className="rounded-2xl xl:col-span-2">
          <CardHeader><CardTitle>Equity Curve</CardTitle></CardHeader>
          <CardContent className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={equity}>
                <defs>
                  <linearGradient id="repGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="currentColor" stopOpacity={0.2} />
                    <stop offset="100%" stopColor="currentColor" stopOpacity={0.02} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                <XAxis dataKey="t" stroke="currentColor" opacity={0.5} />
                <YAxis stroke="currentColor" opacity={0.5} />
                <Tooltip />
                <Area type="monotone" dataKey="v" strokeWidth={2} stroke="currentColor" fill="url(#repGradient)" />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="rounded-2xl">
          <CardHeader><CardTitle>PNL by Instrument</CardTitle></CardHeader>
          <CardContent className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={byInstrument}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                <XAxis dataKey="symbol" stroke="currentColor" opacity={0.5} />
                <YAxis stroke="currentColor" opacity={0.5} />
                <Tooltip />
                <Bar dataKey="pnl" radius={[8,8,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <Card className="rounded-2xl">
        <CardHeader><CardTitle>Raw Snapshot</CardTitle></CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Metric</TableHead>
                <TableHead>Value</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow><TableCell>Data points</TableCell><TableCell>{equity.length}</TableCell></TableRow>
              <TableRow><TableCell>Instruments</TableCell><TableCell>{byInstrument.length}</TableCell></TableRow>
              <TableRow><TableCell>Last update</TableCell><TableCell>—</TableCell></TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
