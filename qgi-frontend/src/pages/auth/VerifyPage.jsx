import { useEffect, useState } from 'react'
import { useSearchParams, Navigate } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
// Optimized icon imports for tree-shaking
import CheckCircle from 'lucide-react/dist/esm/icons/check-circle'
import XCircle from 'lucide-react/dist/esm/icons/x-circle'
import Loader2 from 'lucide-react/dist/esm/icons/loader-2'
import TrendingUp from 'lucide-react/dist/esm/icons/trending-up'
import { useAuth } from '../../App'
import { API_BASE_URL } from '../../config'

export default function VerifyPage() {
  const [searchParams] = useSearchParams()
  const [status, setStatus] = useState('verifying') // verifying, success, error
  const [message, setMessage] = useState('')
  const { login, user } = useAuth()

  const token = searchParams.get('token')

  useEffect(() => {
    if (!token) {
      setStatus('error')
      setMessage('Invalid verification link. Please request a new magic link.')
      return
    }

    verifyToken()
  }, [token])

  const verifyToken = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token }),
      })

      const data = await response.json()

      if (response.ok) {
        setStatus('success')
        setMessage('Successfully signed in! Redirecting to your dashboard...')
        
        // Log the user in
        login(data.access_token, data.user)
        
        // Redirect after a short delay
        setTimeout(() => {
          window.location.href = '/dashboard'
        }, 2000)
      } else {
        setStatus('error')
        setMessage(data.error || 'Failed to verify the magic link. It may have expired.')
      }
    } catch (err) {
      setStatus('error')
      setMessage('Network error. Please try again.')
    }
  }

  // If already logged in, redirect to dashboard
  if (user) {
    return <Navigate to="/dashboard" replace />
  }

  const getIcon = () => {
    switch (status) {
      case 'verifying':
        return <Loader2 className="h-12 w-12 text-primary animate-spin" />
      case 'success':
        return <CheckCircle className="h-12 w-12 text-green-500" />
      case 'error':
        return <XCircle className="h-12 w-12 text-red-500" />
      default:
        return null
    }
  }

  const getTitle = () => {
    switch (status) {
      case 'verifying':
        return 'Verifying your access...'
      case 'success':
        return 'Welcome to QGI Portal!'
      case 'error':
        return 'Verification Failed'
      default:
        return ''
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <div className="bg-primary rounded-full p-3">
              <TrendingUp className="h-8 w-8 text-primary-foreground" />
            </div>
          </div>
          <h1 className="text-3xl font-bold text-foreground">QGI Client Portal</h1>
        </div>

        {/* Verification Card */}
        <Card className="shadow-lg">
          <CardHeader className="text-center">
            <div className="flex justify-center mb-4">
              {getIcon()}
            </div>
            <CardTitle className="text-xl">{getTitle()}</CardTitle>
            <CardDescription>
              {status === 'verifying' && 'Please wait while we verify your magic link...'}
              {status === 'success' && 'You have been successfully authenticated.'}
              {status === 'error' && 'There was a problem with your verification link.'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {message && (
              <Alert variant={status === 'error' ? 'destructive' : 'default'}>
                <AlertDescription>{message}</AlertDescription>
              </Alert>
            )}

            {status === 'error' && (
              <div className="mt-4 space-y-3">
                <Button 
                  onClick={() => window.location.href = '/auth/login'} 
                  className="w-full"
                >
                  Request New Magic Link
                </Button>
                
                <div className="text-center">
                  <p className="text-sm text-muted-foreground">
                    Magic links expire after 10 minutes for security.
                  </p>
                </div>
              </div>
            )}

            {status === 'success' && (
              <div className="mt-4 text-center">
                <div className="animate-pulse">
                  <p className="text-sm text-muted-foreground">
                    Redirecting to your dashboard...
                  </p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center mt-8 text-sm text-muted-foreground">
          <p>Secured by QGI Investment Management</p>
        </div>
      </div>
    </div>
  )
}

