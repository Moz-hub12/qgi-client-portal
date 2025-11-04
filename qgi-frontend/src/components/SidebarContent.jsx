import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
// Optimized icon imports for tree-shaking
import BarChart3 from 'lucide-react/dist/esm/icons/bar-chart-3'
import FileText from 'lucide-react/dist/esm/icons/file-text'
import User from 'lucide-react/dist/esm/icons/user'
import Bell from 'lucide-react/dist/esm/icons/bell'
import HelpCircle from 'lucide-react/dist/esm/icons/help-circle'
import TrendingUp from 'lucide-react/dist/esm/icons/trending-up'
import { getUserInitials } from '../utils/formatters'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: BarChart3 },
  { name: 'Documents', href: '/documents', icon: FileText },
  { name: 'Profile', href: '/profile', icon: User },
  { name: 'Announcements', href: '/announcements', icon: Bell },
  { name: 'Support', href: '/support', icon: HelpCircle },
]

const SidebarContent = ({ user, setSidebarOpen }) => {
  const location = useLocation()

  const isActive = (href) => {
    return location.pathname === href
  }

  return (
    <div className="flex h-full flex-col">
      {/* Logo */}
      <div className="flex h-16 shrink-0 items-center px-6 border-b">
        <div className="flex items-center">
          <div className="bg-primary rounded-lg p-2">
            <TrendingUp className="h-6 w-6 text-primary-foreground" />
          </div>
          <span className="ml-3 text-xl font-bold">QGI Portal</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-2">
        {navigation.map((item) => {
          const Icon = item.icon
          return (
            <Link
              key={item.name}
              to={item.href}
              className={`flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive(item.href)
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:text-foreground hover:bg-muted'
              }`}
              onClick={() => setSidebarOpen && setSidebarOpen(false)}
            >
              <Icon className="mr-3 h-5 w-5" />
              {item.name}
            </Link>
          )
        })}
      </nav>

      {/* User Info */}
      <div className="border-t p-4">
        <div className="flex items-center">
          <Avatar className="h-8 w-8">
            <AvatarFallback>{getUserInitials(user)}</AvatarFallback>
          </Avatar>
          <div className="ml-3 flex-1 min-w-0">
            <p className="text-sm font-medium truncate">
              {user?.name || user?.username || 'User'}
            </p>
            <p className="text-xs text-muted-foreground truncate">
              {user?.email}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default React.memo(SidebarContent)

