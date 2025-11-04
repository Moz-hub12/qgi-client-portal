import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
// Optimized icon imports for tree-shaking
import HelpCircle from 'lucide-react/dist/esm/icons/help-circle'
import MessageSquare from 'lucide-react/dist/esm/icons/message-square'
import FileText from 'lucide-react/dist/esm/icons/file-text'
import DollarSign from 'lucide-react/dist/esm/icons/dollar-sign'
import Settings from 'lucide-react/dist/esm/icons/settings'
import Clock from 'lucide-react/dist/esm/icons/clock'
import CheckCircle from 'lucide-react/dist/esm/icons/check-circle'
import AlertCircle from 'lucide-react/dist/esm/icons/alert-circle'

export default function SupportPage() {
  const [activeTab, setActiveTab] = useState('requests')

  // Mock support requests data
  const mockRequests = [
    {
      id: 1,
      subject: 'Request Monthly Statement',
      type: 'statement',
      status: 'resolved',
      created_at: '2024-08-10T10:00:00Z',
      description: 'Please provide the July 2024 monthly statement.'
    },
    {
      id: 2,
      subject: 'ROI Withdrawal Request',
      type: 'withdrawal',
      status: 'in_progress',
      created_at: '2024-08-08T14:30:00Z',
      description: 'I would like to withdraw my Q2 ROI distribution.'
    },
    {
      id: 3,
      subject: 'Account Access Issue',
      type: 'technical',
      status: 'open',
      created_at: '2024-08-05T09:15:00Z',
      description: 'Having trouble accessing the documents section.'
    }
  ]

  const requestTypes = [
    { value: 'statement', label: 'Request Statement', icon: FileText },
    { value: 'withdrawal', label: 'Withdraw ROI', icon: DollarSign },
    { value: 'general', label: 'General Inquiry', icon: MessageSquare },
    { value: 'kyc', label: 'KYC Support', icon: Settings },
    { value: 'technical', label: 'Technical Issue', icon: HelpCircle }
  ]

  const getStatusColor = (status) => {
    switch (status) {
      case 'resolved':
        return 'default'
      case 'in_progress':
        return 'secondary'
      case 'open':
        return 'destructive'
      default:
        return 'secondary'
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'resolved':
        return <CheckCircle className="h-4 w-4" />
      case 'in_progress':
        return <Clock className="h-4 w-4" />
      case 'open':
        return <AlertCircle className="h-4 w-4" />
      default:
        return <Clock className="h-4 w-4" />
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Support & Requests</h1>
        <p className="text-muted-foreground">
          Get help and submit requests for statements, withdrawals, and more
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList>
          <TabsTrigger value="requests">My Requests</TabsTrigger>
          <TabsTrigger value="new">New Request</TabsTrigger>
        </TabsList>

        <TabsContent value="requests" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Support Requests</CardTitle>
              <CardDescription>
                Track the status of your submitted requests
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {mockRequests.map((request) => (
                  <div key={request.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="space-y-1">
                      <div className="flex items-center space-x-2">
                        <h4 className="font-medium">{request.subject}</h4>
                        <Badge variant={getStatusColor(request.status)} className="flex items-center">
                          {getStatusIcon(request.status)}
                          <span className="ml-1 capitalize">{request.status.replace('_', ' ')}</span>
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">{request.description}</p>
                      <p className="text-xs text-muted-foreground">
                        Submitted on {formatDate(request.created_at)}
                      </p>
                    </div>
                    <Button variant="outline" size="sm">
                      View Details
                    </Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="new" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Submit New Request</CardTitle>
              <CardDescription>
                Choose the type of support you need
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {requestTypes.map((type) => {
                  const Icon = type.icon
                  return (
                    <Card key={type.value} className="cursor-pointer hover:shadow-md transition-shadow">
                      <CardContent className="flex flex-col items-center justify-center p-6 text-center">
                        <Icon className="h-8 w-8 mb-3 text-primary" />
                        <h3 className="font-medium">{type.label}</h3>
                      </CardContent>
                    </Card>
                  )
                })}
              </div>
              
              <div className="mt-6 p-4 bg-muted rounded-lg">
                <p className="text-sm text-muted-foreground text-center">
                  <HelpCircle className="inline h-4 w-4 mr-1" />
                  Full request form functionality will be implemented in Phase 7
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Contact Information */}
      <Card>
        <CardHeader>
          <CardTitle>Contact Information</CardTitle>
          <CardDescription>
            Alternative ways to reach our support team
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <h4 className="font-medium">Email Support</h4>
              <p className="text-sm text-muted-foreground">admin@quantumgrowthinvestments.com</p>
              <p className="text-xs text-muted-foreground">Response within 24 hours</p>
            </div>
            <div className="space-y-2">
              <h4 className="font-medium">Phone Support</h4>
              <p className="text-sm text-muted-foreground">+1 (343) 999-8073</p>
              <p className="text-xs text-muted-foreground">Monday - Friday, 9 AM - 5 PM EST</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

