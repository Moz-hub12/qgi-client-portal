import React from "react"
// Removed framer-motion import (not installed in admin)
// Optimized icon imports for tree-shaking
import LayoutGrid from "lucide-react/dist/esm/icons/layout-grid"
import LineChart from "lucide-react/dist/esm/icons/line-chart"
import BarChart3 from "lucide-react/dist/esm/icons/bar-chart-3"
import ArrowUpRight from "lucide-react/dist/esm/icons/arrow-up-right"
import Users from "lucide-react/dist/esm/icons/users"
import Building2 from "lucide-react/dist/esm/icons/building-2"
import ShieldCheck from "lucide-react/dist/esm/icons/shield-check"
import ChevronDown from "lucide-react/dist/esm/icons/chevron-down"
import Search from "lucide-react/dist/esm/icons/search"
import Bell from "lucide-react/dist/esm/icons/bell"
import Menu from "lucide-react/dist/esm/icons/menu"
import LogOut from "lucide-react/dist/esm/icons/log-out"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuLabel,
} from "@/components/ui/dropdown-menu"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { ResponsiveContainer, Line, XAxis, YAxis, CartesianGrid, Tooltip, AreaChart, Area, BarChart, Bar } from "recharts"

/**
 * QGI Admin — High‑level preview of a modern, premium admin UI.
 * - Tailwind for styling
 * - shadcn/ui components for consistency
 * - lucide-react icons (optimized for tree-shaking)
 * - Optimized for performance
 * - recharts for quick data viz
 *
 * Drop this into a route like /dashboard and wire your real data.
 */

const revenueData = [
  { month: "Jan", value: 12 },
  { month: "Feb", value: 15 },
  { month: "Mar", value: 18 },
  { month: "Apr", value: 14 },
  { month: "May", value: 22 },
  { month: "Jun", value: 26 },
  { month: "Jul", value: 24 },
]

const barData = [
  { name: "EUR/USD", pnl: 12 },
  { name: "USD/CAD", pnl: 6 },
  { name: "GBP/USD", pnl: 10 },
  { name: "AUD/NZD", pnl: 3 },
  { name: "NZD/USD", pnl: 7 },
]

const recent = [
  { id: "INV-10021", client: "A. Laurent", amount: 25000, status: "Pending KYC" },
  { id: "INV-10018", client: "J. Patel", amount: 10000, status: "Active" },
  { id: "INV-10016", client: "S. Moore", amount: 5000, status: "Flagged" },
  { id: "INV-10012", client: "D. Chen", amount: 3000, status: "Active" },
]

function Sidebar() {
  const nav = [
    { label: "Dashboard", icon: LayoutGrid },
    { label: "Clients", icon: Users },
    { label: "Accounts", icon: Building2 },
    { label: "Compliance", icon: ShieldCheck },
    { label: "Reports", icon: BarChart3 },
  ]
  return (
    <aside className="hidden md:flex md:flex-col w-64 shrink-0 border-r bg-gradient-to-b from-slate-950 to-slate-900 text-slate-100">
      <div className="h-16 flex items-center px-6 border-b border-white/10">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-amber-400 to-amber-600" />
          <span className="tracking-wide font-semibold">Quantum Growth</span>
        </div>
      </div>
      <nav className="p-3 space-y-1">
        {nav.map((n, i) => (
          <button
            key={n.label}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-xl text-sm hover:bg-white/5 transition ${
              i === 0 ? "bg-white/5" : ""
            }`}
          >
            <n.icon className="h-4 w-4" />
            {n.label}
          </button>
        ))}
      </nav>
      <div className="mt-auto p-4 text-xs text-slate-400">© {new Date().getFullYear()} QGI</div>
    </aside>
  )
}

function TopBar() {
  return (
    <div className="h-16 border-b bg-white dark:bg-slate-950/60 backdrop-blur supports-[backdrop-filter]:bg-white/60 sticky top-0 z-10">
      <div className="h-full px-4 md:px-8 flex items-center justify-between">
        <div className="flex items-center gap-2 md:gap-3">
          <Button variant="ghost" size="icon" className="md:hidden"><Menu className="h-5 w-5" /></Button>
          <h1 className="text-xl md:text-2xl font-semibold tracking-tight">Admin Dashboard</h1>
        </div>
        <div className="flex items-center gap-2 md:gap-3">
          <div className="hidden md:flex items-center gap-2">
            <div className="relative">
              <Input placeholder="Search…" className="pl-9 w-56 rounded-xl" />
              <Search className="h-4 w-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
            </div>
            <Button variant="ghost" size="icon" className="rounded-xl"><Bell className="h-5 w-5" /></Button>
          </div>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" className="rounded-xl">
                <Avatar className="h-6 w-6 mr-2"><AvatarFallback>AD</AvatarFallback></Avatar>
                Admin
                <ChevronDown className="ml-2 h-4 w-4 opacity-60" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-48 rounded-xl">
              <DropdownMenuLabel>My Account</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem>Profile</DropdownMenuItem>
              <DropdownMenuItem>Settings</DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="text-red-600"><LogOut className="h-4 w-4 mr-2"/>Sign out</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </div>
  )
}

function StatCard({ icon: Icon, title, value, delta }) {
  return (
    <Card className="rounded-2xl shadow-sm">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-slate-600">{title}</CardTitle>
        <Icon className="h-4 w-4 text-amber-500" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-semibold">{value}</div>
        <div className="text-xs text-emerald-600 mt-1 flex items-center gap-1"><ArrowUpRight className="h-3 w-3" /> {delta}</div>
      </CardContent>
    </Card>
  )
}

function ChartCard() {
  return (
    <Card className="rounded-2xl">
      <CardHeader>
        <CardTitle>Equity Curve</CardTitle>
      </CardHeader>
      <CardContent className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={revenueData} margin={{ top: 10, left: 0, right: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="qgiGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="currentColor" stopOpacity={0.2} />
                <stop offset="100%" stopColor="currentColor" stopOpacity={0.02} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
            <XAxis dataKey="month" stroke="currentColor" opacity={0.5} />
            <YAxis stroke="currentColor" opacity={0.5} />
            <Tooltip />
            <Area type="monotone" dataKey="value" strokeWidth={2} stroke="currentColor" fill="url(#qgiGradient)" />
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

function BarCard() {
  return (
    <Card className="rounded-2xl">
      <CardHeader>
        <CardTitle>PNL by Instrument</CardTitle>
      </CardHeader>
      <CardContent className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={barData}>
            <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
            <XAxis dataKey="name" stroke="currentColor" opacity={0.5} />
            <YAxis stroke="currentColor" opacity={0.5} />
            <Tooltip />
            <Bar dataKey="pnl" radius={[8,8,0,0]} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

function RecentTable() {
  return (
    <Card className="rounded-2xl">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Recent Activity</CardTitle>
        <div className="flex gap-2">
          <Input placeholder="Filter…" className="h-9 w-48 rounded-xl" />
          <Button className="rounded-xl">Export</Button>
        </div>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>Client</TableHead>
              <TableHead className="text-right">Amount</TableHead>
              <TableHead>Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {recent.map((r) => (
              <TableRow key={r.id}>
                <TableCell className="font-medium">{r.id}</TableCell>
                <TableCell>{r.client}</TableCell>
                <TableCell className="text-right">${r.amount.toLocaleString()}</TableCell>
                <TableCell>
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    r.status === 'Active' ? 'bg-emerald-100 text-emerald-700' :
                    r.status === 'Flagged' ? 'bg-rose-100 text-rose-700' : 'bg-amber-100 text-amber-700'
                  }`}>{r.status}</span>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}

export default function QGIAdminRedesign() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-white dark:from-slate-950 dark:to-slate-900 text-slate-900 dark:text-slate-100">
      <div className="flex">
        <Sidebar />
        <main className="flex-1">
          <TopBar />
<section className="p-8 space-y-6">
            {/* KPI cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
              <StatCard icon={Users} title="Active Clients" value="142" delta="+4.2%" />
              <StatCard icon={BarChart3} title="MTD Return" value="3.1%" delta="+0.4%" />
              <StatCard icon={ShieldCheck} title="Compliance Flags" value="3" delta="-1 this week" />
              <StatCard icon={Building2} title="AUM (USD)" value="$2.4M" delta="+$120k" />
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
              <div className="xl:col-span-2"><ChartCard /></div>
              <div className="xl:col-span-1"><BarCard /></div>
            </div>

            {/* Table */}
            <RecentTable />
          </section>
        </main>
      </div>
    </div>
  )
}

