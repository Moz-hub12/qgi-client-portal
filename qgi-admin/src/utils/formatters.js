/**
 * QGI Admin - Utility Functions
 * Formatting and helper functions for the admin dashboard
 */

/**
 * Format a number as currency (USD)
 * @param {number} amount - The amount to format
 * @param {boolean} compact - Use compact notation for large numbers
 * @returns {string} Formatted currency string
 */
export const formatCurrency = (amount, compact = false) => {
  if (amount === null || amount === undefined) return '$0.00'
  
  const num = Number(amount)
  if (!Number.isFinite(num)) return '$0.00'
  
  if (compact && Math.abs(num) >= 1000) {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      notation: 'compact',
      maximumFractionDigits: 1
    }).format(num)
  }
  
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(num)
}

/**
 * Format a date string consistently
 * @param {string|Date} dateString - The date to format
 * @param {string} format - Format type: 'short', 'long', or 'datetime'
 * @returns {string} Formatted date string
 */
export const formatDate = (dateString, format = 'short') => {
  if (!dateString) return '—'
  
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return '—'
  
  switch (format) {
    case 'long':
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    case 'datetime':
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    case 'short':
    default:
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
  }
}

/**
 * Get user initials from user object
 * @param {Object} user - User object with name, username, or email
 * @returns {string} User initials (2 characters)
 */
export const getUserInitials = (user) => {
  if (!user) return 'AD'
  
  // Try to get from name first
  if (user.name) {
    const parts = user.name.trim().split(' ')
    if (parts.length >= 2) {
      return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
    }
    return user.name.substring(0, 2).toUpperCase()
  }
  
  // Fall back to username
  if (user.username) {
    return user.username.substring(0, 2).toUpperCase()
  }
  
  // Fall back to email
  if (user.email) {
    return user.email.substring(0, 2).toUpperCase()
  }
  
  return 'AD'
}

/**
 * Format a percentage value
 * @param {number} value - The percentage value (0-100 or 0-1)
 * @param {boolean} isDecimal - Whether the value is in decimal form (0-1)
 * @param {number} decimals - Number of decimal places
 * @returns {string} Formatted percentage string
 */
export const formatPercentage = (value, isDecimal = false, decimals = 2) => {
  if (value === null || value === undefined) return '0%'
  
  const num = Number(value)
  if (!Number.isFinite(num)) return '0%'
  
  const percentage = isDecimal ? num * 100 : num
  return `${percentage.toFixed(decimals)}%`
}

/**
 * Format a large number with K/M/B suffix
 * @param {number} num - The number to format
 * @param {number} decimals - Number of decimal places
 * @returns {string} Formatted number string
 */
export const formatCompactNumber = (num, decimals = 1) => {
  if (num === null || num === undefined) return '0'
  
  const n = Number(num)
  if (!Number.isFinite(n)) return '0'
  
  if (Math.abs(n) >= 1e9) {
    return (n / 1e9).toFixed(decimals) + 'B'
  }
  if (Math.abs(n) >= 1e6) {
    return (n / 1e6).toFixed(decimals) + 'M'
  }
  if (Math.abs(n) >= 1e3) {
    return (n / 1e3).toFixed(decimals) + 'K'
  }
  return n.toFixed(decimals)
}

/**
 * Get status badge color classes
 * @param {string} status - Status string
 * @returns {string} Tailwind CSS classes for badge
 */
export const getStatusBadgeClass = (status) => {
  const statusLower = String(status).toLowerCase()
  
  switch (statusLower) {
    case 'active':
    case 'approved':
    case 'completed':
      return 'bg-emerald-100 text-emerald-700'
    case 'pending':
    case 'pending kyc':
    case 'in_progress':
      return 'bg-amber-100 text-amber-700'
    case 'flagged':
    case 'rejected':
    case 'suspended':
      return 'bg-rose-100 text-rose-700'
    case 'inactive':
    case 'closed':
      return 'bg-slate-100 text-slate-700'
    default:
      return 'bg-blue-100 text-blue-700'
  }
}

/**
 * Safely parse a number from various input types
 * @param {any} value - Value to parse
 * @param {number} fallback - Fallback value if parsing fails
 * @returns {number} Parsed number or fallback
 */
export const safeNumber = (value, fallback = 0) => {
  const num = Number(value)
  return Number.isFinite(num) ? num : fallback
}

/**
 * Truncate text to a maximum length
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length
 * @param {string} suffix - Suffix to add when truncated
 * @returns {string} Truncated text
 */
export const truncateText = (text, maxLength = 50, suffix = '...') => {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength - suffix.length) + suffix
}

/**
 * Calculate relative time from a date
 * @param {string|Date} dateString - The date to compare
 * @returns {string} Relative time string (e.g., "2 hours ago")
 */
export const getRelativeTime = (dateString) => {
  if (!dateString) return '—'
  
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return '—'
  
  const now = new Date()
  const diffMs = now - date
  const diffSec = Math.floor(diffMs / 1000)
  const diffMin = Math.floor(diffSec / 60)
  const diffHour = Math.floor(diffMin / 60)
  const diffDay = Math.floor(diffHour / 24)
  
  if (diffSec < 60) return 'just now'
  if (diffMin < 60) return `${diffMin} minute${diffMin !== 1 ? 's' : ''} ago`
  if (diffHour < 24) return `${diffHour} hour${diffHour !== 1 ? 's' : ''} ago`
  if (diffDay < 30) return `${diffDay} day${diffDay !== 1 ? 's' : ''} ago`
  
  return formatDate(dateString, 'short')
}

