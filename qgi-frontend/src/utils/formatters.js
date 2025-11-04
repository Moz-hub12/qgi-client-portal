/**
 * Utility functions for formatting data
 */

/**
 * Format a number as USD currency
 * @param {number} amount - The amount to format
 * @returns {string} Formatted currency string
 */
export const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

/**
 * Format a date string to a readable format
 * @param {string} dateString - The date string to format
 * @returns {string} Formatted date string
 */
export const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

/**
 * Get user initials from name or email
 * @param {Object} user - User object with name and/or email
 * @returns {string} User initials
 */
export const getUserInitials = (user) => {
  if (user?.name) {
    return user.name.split(' ').map(n => n[0]).join('').toUpperCase()
  }
  return user?.email?.charAt(0).toUpperCase() || 'U'
}

