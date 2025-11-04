import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
// Optimized icon imports for tree-shaking
import User from 'lucide-react/dist/esm/icons/user'
import Shield from 'lucide-react/dist/esm/icons/shield'
import Upload from 'lucide-react/dist/esm/icons/upload'
import CheckCircle from 'lucide-react/dist/esm/icons/check-circle'
import Clock from 'lucide-react/dist/esm/icons/clock'
import { useAuth } from '../App'

export default function ProfilePage() {
  const { user } = useAuth()

  const getKycStatusColor = (status) => {
    switch (status) {
      case 'approved':
        return 'default'
      case 'pending':
        return 'secondary'
      case 'rejected':
        return 'destructive'
      default:
        return 'secondary'
    }
  }

  const getKycStatusIcon = (status) => {
    switch (status) {
      case 'approved':
        return <CheckCircle className="h-4 w-4" />
      case 'pending':
        return <Clock className="h-4 w-4" />
      default:
        return <Clock className="h-4 w-4" />
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Profile & KYC</h1>
        <p className="text-muted-foreground">
          Manage your profile information and KYC documentation
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Profile Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <User className="mr-2 h-5 w-5" />
              Profile Information
            </CardTitle>
            <CardDescription>
              Your account details (read-only for now)
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium text-muted-foreground">Email</label>
              <p className="text-sm">{user?.email}</p>
            </div>
            
            <div>
              <label className="text-sm font-medium text-muted-foreground">Username</label>
              <p className="text-sm">{user?.username}</p>
            </div>
            
            <div>
              <label className="text-sm font-medium text-muted-foreground">Full Name</label>
              <p className="text-sm">{user?.name || 'Not provided'}</p>
            </div>
            
            <div>
              <label className="text-sm font-medium text-muted-foreground">Investor ID</label>
              <p className="text-sm">{user?.investor_id || 'Not assigned'}</p>
            </div>
            
            <div>
              <label className="text-sm font-medium text-muted-foreground">Member Since</label>
              <p className="text-sm">
                {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'Unknown'}
              </p>
            </div>
            
            <div>
              <label className="text-sm font-medium text-muted-foreground">Last Login</label>
              <p className="text-sm">
                {user?.last_login ? new Date(user.last_login).toLocaleDateString() : 'First time'}
              </p>
            </div>
          </CardContent>
        </Card>

        {/* KYC Status */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Shield className="mr-2 h-5 w-5" />
              KYC Status
            </CardTitle>
            <CardDescription>
              Know Your Customer verification status
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Verification Status</span>
              <Badge variant={getKycStatusColor(user?.kyc_status)} className="flex items-center">
                {getKycStatusIcon(user?.kyc_status)}
                <span className="ml-1 capitalize">{user?.kyc_status || 'pending'}</span>
              </Badge>
            </div>

            <div className="space-y-3">
              <div className="text-sm text-muted-foreground">
                {user?.kyc_status === 'approved' && (
                  <p>✅ Your identity has been verified and approved.</p>
                )}
                {user?.kyc_status === 'pending' && (
                  <p>⏳ Your KYC verification is pending review.</p>
                )}
                {user?.kyc_status === 'rejected' && (
                  <p>❌ Your KYC verification was rejected. Please contact support.</p>
                )}
              </div>

              {user?.kyc_status !== 'approved' && (
                <div className="space-y-3">
                  <div className="border-2 border-dashed border-muted rounded-lg p-6 text-center">
                    <Upload className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
                    <p className="text-sm font-medium">Upload ID Proof</p>
                    <p className="text-xs text-muted-foreground">
                      Optional for later implementation
                    </p>
                  </div>
                  
                  <Button variant="outline" className="w-full" disabled>
                    <Upload className="mr-2 h-4 w-4" />
                    Upload Documents
                  </Button>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Additional Information */}
      <Card>
        <CardHeader>
          <CardTitle>Additional Information</CardTitle>
          <CardDescription>
            Extended profile data and preferences
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <User className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <h3 className="text-lg font-medium mb-2">Extended Profile Features</h3>
            <p className="text-muted-foreground mb-4">
              Additional profile management features will be added in future updates
            </p>
            <p className="text-sm text-muted-foreground">
              Including: Preferences, Contact Information, and Account Settings
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

