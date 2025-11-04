import { useState, useEffect, useCallback, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
// Optimized icon imports for tree-shaking
import TrendingUp from 'lucide-react/dist/esm/icons/trending-up'
import DollarSign from 'lucide-react/dist/esm/icons/dollar-sign'
import Calendar from 'lucide-react/dist/esm/icons/calendar'
import FileText from 'lucide-react/dist/esm/icons/file-text'
import ArrowUpRight from 'lucide-react/dist/esm/icons/arrow-up-right'
import ArrowDownRight from 'lucide-react/dist/esm/icons/arrow-down-right'
import PieChart from 'lucide-react/dist/esm/icons/pie-chart'
import BarChart3 from 'lucide-react/dist/esm/icons/bar-chart-3'
import MessageSquare from 'lucide-react/dist/esm/icons/message-square'
import User from 'lucide-react/dist/esm/icons/user'
import Bell from 'lucide-react/dist/esm/icons/bell'
import Download from 'lucide-react/dist/esm/icons/download'
import RefreshCw from 'lucide-react/dist/esm/icons/refresh-cw'

import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  AreaChart,
  Area
} from 'recharts'
import { useAuth } from '../App'
import { API_BASE_URL } from '../config'
import { formatCurrency, formatDate } from '../utils/formatters'

export default function DashboardPage() {
  const { user, token } = useAuth()
  const navigate = useNavigate()
  const [dashboardData, setDashboardData] = useState(null)
  const [performanceHistory, setPerformanceHistory] = useState([])
  const [assetAllocation, setAssetAllocation] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [refreshing, setRefreshing] = useState(false)

  // Memoize the fetch function to prevent unnecessary re-creations
  const fetchDashboardData = useCallback(async () => {
    const response = await fetch(`${API_BASE_URL}/api/investor/dashboard`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) {
      throw new Error(`Dashboard API error: ${response.status}`)
    }
    
    const data = await response.json()
    setDashboardData(data)
    
    // Extract performance history from performance_series
    if (data.performance_series && data.performance_series.points) {
      setPerformanceHistory(data.performance_series.points)
    }
    
    // Extract asset allocation
    if (data.asset_allocation) {
      const allocationArray = Object.entries(data.asset_allocation).map(([name, value]) => ({
        name,
        value
      }))
      setAssetAllocation(allocationArray)
    }
  }, [token])

  const loadDashboardData = useCallback(async () => {
    setLoading(true)
    setError(null)
    
    try {
      await fetchDashboardData()
    } catch (err) {
      setError('Failed to load dashboard data. Please try again.')
      // Only log errors in development
      if (import.meta.env.DEV) {
        console.error('Dashboard loading error:', err)
      }
    } finally {
      setLoading(false)
    }
  }, [fetchDashboardData])

  useEffect(() => {
    loadDashboardData()
  }, [loadDashboardData])

  const handleRefresh = useCallback(async () => {
    setRefreshing(true)
    await loadDashboardData()
    setRefreshing(false)
  }, [loadDashboardData])

  // Memoize button handlers to prevent re-creation on every render
  const handleRequestStatement = useCallback(() => {
    navigate('/support', { state: { requestType: 'statement' } })
  }, [navigate])

  const handleWithdrawROI = useCallback(() => {
    navigate('/support', { state: { requestType: 'withdrawal' } })
  }, [navigate])

  const handleScheduleMeeting = useCallback(() => {
    navigate('/support', { state: { requestType: 'meeting' } })
  }, [navigate])

  const handleViewFullReport = useCallback(() => {
    navigate('/documents')
  }, [navigate])

  const handleViewActivity = useCallback((activity) => {
    if (activity.type === 'statement') {
      navigate('/documents')
    } else if (activity.type === 'contribution' || activity.type === 'performance') {
      navigate('/support', { state: { requestType: 'inquiry', subject: activity.title } })
    }
  }, [navigate])

  // Memoize chart colors to prevent re-creation
  const CHART_COLORS = useMemo(() => ['#0088FE', '#00C49F', '#FFBB28'], [])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading your portfolio...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <Alert variant="destructive" className="max-w-md mx-auto">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
        <Button onClick={loadDashboardData} variant="outline" className="mt-4">
          <RefreshCw className="mr-2 h-4 w-4" />
          Try Again
        </Button>
      </div>
    )
  }

  if (!dashboardData) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">No dashboard data available.</p>
        <Button onClick={loadDashboardData} variant="outline" className="mt-4">
          <RefreshCw className="mr-2 h-4 w-4" />
          Reload
        </Button>
      </div>
    )
  }

  // Use dashboardData directly - no portfolio wrapper

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Welcome back, {user?.name || user?.email || 'Investor'}
          </h1>
          <p className="text-muted-foreground">
            Here's an overview of your investment portfolio
          </p>
        </div>
        <Button 
          onClick={handleRefresh} 
          variant="outline" 
          size="sm"
          disabled={refreshing}
        >
          <RefreshCw className={`mr-2 h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Current Value</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(dashboardData.current_value)}</div>
            <p className="text-xs text-muted-foreground">
              Total portfolio value
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Contributions</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(dashboardData.total_contributions)}</div>
            <p className="text-xs text-muted-foreground">
              Amount invested
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Profit/Loss</CardTitle>
            {dashboardData.profit_loss >= 0 ? (
              <ArrowUpRight className="h-4 w-4 text-green-600" />
            ) : (
              <ArrowDownRight className="h-4 w-4 text-red-600" />
            )}
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${dashboardData.profit_loss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {formatCurrency(dashboardData.profit_loss)}
            </div>
            <p className="text-xs text-muted-foreground">
              <Badge variant={dashboardData.profit_loss >= 0 ? 'default' : 'destructive'} className="text-xs">
                {dashboardData.profit_loss >= 0 ? '+' : ''}{dashboardData.profit_loss_percentage.toFixed(2)}%
              </Badge>
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Next Lock Date</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {dashboardData.next_lock_date ? new Date(dashboardData.next_lock_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : 'TBD'}
            </div>
            <p className="text-xs text-muted-foreground">
              {dashboardData.next_lock_date ? formatDate(dashboardData.next_lock_date) : 'Not set'}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row */}
      <div className="grid gap-4 md:grid-cols-2">
        {/* Performance Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Performance History</CardTitle>
            <CardDescription>Your portfolio value over time</CardDescription>
          </CardHeader>
          <CardContent>
            {performanceHistory.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={performanceHistory}>
                  <defs>
                    <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#8884d8" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Area type="monotone" dataKey="value" stroke="#8884d8" fillOpacity={1} fill="url(#colorValue)" />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-[300px] text-muted-foreground">
                No performance data available yet
              </div>
            )}
          </CardContent>
        </Card>

        {/* Asset Allocation Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Asset Allocation</CardTitle>
            <CardDescription>Distribution of your investments</CardDescription>
          </CardHeader>
          <CardContent>
            {assetAllocation.length > 0 && assetAllocation.some(item => item.value > 0) ? (
              <ResponsiveContainer width="100%" height={300}>
                <RechartsPieChart>
                  <Pie
                    data={assetAllocation}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {assetAllocation.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </RechartsPieChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-[300px] text-muted-foreground">
                No allocation data available yet
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Manage your investment account</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <Button onClick={handleRequestStatement} variant="outline" className="w-full">
              <FileText className="mr-2 h-4 w-4" />
              Request Statement
            </Button>
            <Button onClick={handleWithdrawROI} variant="outline" className="w-full">
              <Download className="mr-2 h-4 w-4" />
              Withdraw ROI
            </Button>
            <Button onClick={handleScheduleMeeting} variant="outline" className="w-full">
              <Calendar className="mr-2 h-4 w-4" />
              Schedule Meeting
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

