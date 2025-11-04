# QGI Backend - API Documentation

Complete API reference for all endpoints.

---

## Base URL

```
Production: https://qgi-backend.onrender.com
Local: http://localhost:5000
```

---

## Authentication

### Client Authentication
Uses JWT tokens obtained from login endpoint.

**Header:**
```
Authorization: Bearer <jwt_token>
```

### Admin Authentication
Uses JWT tokens obtained from admin login endpoint.

**Header:**
```
Authorization: Bearer <admin_jwt_token>
```

---

## Client Portal Endpoints

### Authentication

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "name": "John Doe"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user_id": 123
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "user": {
    "id": 123,
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

---

### User Management

#### Get User Profile
```http
GET /api/user/profile
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "id": 123,
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2025-01-01T00:00:00Z"
}
```

#### Update User Profile
```http
PUT /api/user/profile
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "name": "John Updated Doe",
  "phone": "+1234567890"
}
```

---

### Investor Data

#### Get Dashboard Data
```http
GET /api/investor/dashboard
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "current_value": 100000.00,
  "initial_investment": 80000.00,
  "total_return": 20000.00,
  "roi": 25.0,
  "ytd_return": 15.5,
  "last_updated": "2025-11-04T12:00:00Z"
}
```

#### Get Performance History
```http
GET /api/investor/performance?period=1y
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "data": [
    {
      "date": "2025-01-01",
      "value": 80000.00
    },
    {
      "date": "2025-11-04",
      "value": 100000.00
    }
  ]
}
```

---

### Documents

#### List Documents
```http
GET /api/documents
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "documents": [
    {
      "id": 1,
      "title": "Q3 2025 Statement",
      "type": "statement",
      "uploaded_at": "2025-10-01T00:00:00Z",
      "file_url": "https://..."
    }
  ]
}
```

#### Upload Document
```http
POST /api/documents/upload
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data

file: <file_data>
title: "Document Title"
type: "statement"
```

---

### Announcements

#### List Announcements
```http
GET /api/announcements
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "announcements": [
    {
      "id": 1,
      "title": "Q3 Results",
      "content": "Great quarter...",
      "created_at": "2025-10-15T00:00:00Z",
      "priority": "high"
    }
  ]
}
```

---

### Support

#### List Support Tickets
```http
GET /api/support/tickets
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "tickets": [
    {
      "id": 1,
      "subject": "Account Question",
      "status": "open",
      "created_at": "2025-11-01T00:00:00Z",
      "last_message": "How do I..."
    }
  ]
}
```

#### Create Support Ticket
```http
POST /api/support/tickets
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "subject": "Account Question",
  "message": "How do I update my profile?",
  "priority": "normal"
}
```

---

## Admin Dashboard Endpoints

### Admin Authentication

#### Admin Login
```http
POST /api/admin/auth/login
Content-Type: application/json

{
  "email": "admin@qgi.com",
  "password": "admin_password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "admin": {
    "id": 1,
    "email": "admin@qgi.com",
    "name": "Admin User",
    "permissions": ["view_clients", "edit_clients", ...]
  }
}
```

---

### Client Management

#### List All Clients
```http
GET /api/admin/clients?page=1&per_page=20&search=john
Authorization: Bearer <admin_jwt_token>
```

**Response:**
```json
{
  "clients": [
    {
      "id": 123,
      "name": "John Doe",
      "email": "john@example.com",
      "current_value": 100000.00,
      "roi": 25.0,
      "status": "active",
      "kyc_status": "approved"
    }
  ],
  "total": 150,
  "page": 1,
  "per_page": 20
}
```

#### Get Client Details
```http
GET /api/admin/clients/123
Authorization: Bearer <admin_jwt_token>
```

**Response:**
```json
{
  "id": 123,
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "current_value": 100000.00,
  "initial_investment": 80000.00,
  "roi": 25.0,
  "kyc_status": "approved",
  "created_at": "2025-01-01T00:00:00Z",
  "last_login": "2025-11-04T10:00:00Z"
}
```

#### Update Client
```http
PUT /api/admin/clients/123
Authorization: Bearer <admin_jwt_token>
Content-Type: application/json

{
  "name": "John Updated Doe",
  "phone": "+1234567890",
  "kyc_status": "approved"
}
```

---

### Compliance Management (NEW)

#### List Compliance Flags
```http
GET /api/admin/compliance/flags?severity=high&status=open&user_id=123
Authorization: Bearer <admin_jwt_token>
```

**Query Parameters:**
- `severity` - Filter by severity (low, medium, high, critical)
- `status` - Filter by status (open, investigating, resolved)
- `user_id` - Filter by specific user

**Response:**
```json
{
  "flags": [
    {
      "id": 1,
      "user_id": 123,
      "user_name": "John Doe",
      "flag_type": "kyc_incomplete",
      "severity": "high",
      "status": "open",
      "description": "KYC documents missing",
      "created_at": "2025-11-01T00:00:00Z",
      "updated_at": "2025-11-04T00:00:00Z",
      "assigned_to": "admin@qgi.com"
    }
  ],
  "total": 5
}
```

#### Create Compliance Flag
```http
POST /api/admin/compliance/flags
Authorization: Bearer <admin_jwt_token>
Content-Type: application/json

{
  "user_id": 123,
  "flag_type": "kyc_incomplete",
  "severity": "high",
  "description": "Missing passport scan",
  "assigned_to": "admin@qgi.com"
}
```

**Response:**
```json
{
  "message": "Compliance flag created",
  "flag_id": 1
}
```

#### Update Compliance Flag
```http
PUT /api/admin/compliance/flags/1
Authorization: Bearer <admin_jwt_token>
Content-Type: application/json

{
  "status": "resolved",
  "resolution_notes": "Documents received and verified"
}
```

#### Delete Compliance Flag
```http
DELETE /api/admin/compliance/flags/1
Authorization: Bearer <admin_jwt_token>
```

#### Get KYC Status Overview
```http
GET /api/admin/compliance/kyc-status
Authorization: Bearer <admin_jwt_token>
```

**Response:**
```json
{
  "pending": 5,
  "approved": 120,
  "rejected": 3,
  "expired": 2,
  "total": 130
}
```

#### Update User KYC Status
```http
PUT /api/admin/compliance/kyc-status/123
Authorization: Bearer <admin_jwt_token>
Content-Type: application/json

{
  "kyc_status": "approved",
  "notes": "All documents verified"
}
```

#### Get Compliance Statistics
```http
GET /api/admin/compliance/stats
Authorization: Bearer <admin_jwt_token>
```

**Response:**
```json
{
  "total_flags": 25,
  "open_flags": 10,
  "critical_flags": 2,
  "flags_by_type": {
    "kyc_incomplete": 8,
    "suspicious_activity": 2,
    "document_expired": 5
  },
  "flags_by_severity": {
    "low": 10,
    "medium": 8,
    "high": 5,
    "critical": 2
  }
}
```

---

### Reports & Analytics (NEW)

#### Get Dashboard Statistics
```http
GET /api/admin/reports/dashboard-stats
Authorization: Bearer <admin_jwt_token>
```

**Response:**
```json
{
  "total_aum": 5000000.00,
  "active_clients": 150,
  "avg_roi": 12.5,
  "total_deposits": 4800000.00,
  "total_withdrawals": 200000.00,
  "pending_kyc": 5,
  "open_tickets": 12,
  "compliance_flags": 8
}
```

#### Get Equity Curve
```http
GET /api/admin/reports/equity-curve?start_date=2025-01-01&end_date=2025-11-04
Authorization: Bearer <admin_jwt_token>
```

**Query Parameters:**
- `start_date` - Start date (YYYY-MM-DD)
- `end_date` - End date (YYYY-MM-DD)

**Response:**
```json
{
  "data": [
    {
      "date": "2025-01-01",
      "total_aum": 4500000.00,
      "client_count": 140
    },
    {
      "date": "2025-11-04",
      "total_aum": 5000000.00,
      "client_count": 150
    }
  ]
}
```

#### Get P&L Report
```http
GET /api/admin/reports/pnl-report?start_date=2025-01-01&end_date=2025-11-04
Authorization: Bearer <admin_jwt_token>
```

**Response:**
```json
{
  "total_profit": 625000.00,
  "total_loss": 50000.00,
  "net_pnl": 575000.00,
  "avg_return": 12.5,
  "best_performer": {
    "user_id": 123,
    "name": "John Doe",
    "return": 35.0
  },
  "worst_performer": {
    "user_id": 456,
    "name": "Jane Smith",
    "return": -2.5
  }
}
```

#### Get Client Activity Report
```http
GET /api/admin/reports/client-activity?days=30
Authorization: Bearer <admin_jwt_token>
```

**Query Parameters:**
- `days` - Number of days to look back (default: 30)

**Response:**
```json
{
  "active_users": 120,
  "new_registrations": 10,
  "logins": 450,
  "document_downloads": 89,
  "support_tickets": 15,
  "activity_by_day": [
    {
      "date": "2025-11-01",
      "logins": 45,
      "active_users": 38
    }
  ]
}
```

#### Export to CSV
```http
GET /api/admin/reports/export-csv?report_type=clients&start_date=2025-01-01&end_date=2025-11-04
Authorization: Bearer <admin_jwt_token>
```

**Query Parameters:**
- `report_type` - Type of report (clients, transactions, compliance, activity)
- `start_date` - Start date (YYYY-MM-DD)
- `end_date` - End date (YYYY-MM-DD)

**Response:** CSV file download

**CSV Columns (clients):**
```
User ID,Name,Email,Current Value,ROI,Status,KYC Status,Created At
123,John Doe,john@example.com,100000.00,25.0,active,approved,2025-01-01
```

---

### Permission Management (NEW)

#### Fix Admin Permissions
```http
POST /api/admin/setup/fix-permissions
Authorization: Bearer <admin_jwt_token>
```

**Response:**
```json
{
  "message": "Permissions fixed successfully",
  "admins_updated": 3,
  "permissions_granted": [
    "view_clients",
    "edit_clients",
    "view_compliance",
    "manage_compliance",
    "view_reports",
    "manage_notifications"
  ]
}
```

#### Check Permissions
```http
GET /api/admin/setup/check-permissions
Authorization: Bearer <admin_jwt_token>
```

**Response:**
```json
{
  "admin_id": 1,
  "email": "admin@qgi.com",
  "permissions": [
    "view_clients",
    "edit_clients",
    "view_compliance",
    "manage_compliance",
    "view_reports",
    "manage_notifications"
  ],
  "missing_permissions": []
}
```

#### Grant Specific Permissions
```http
POST /api/admin/setup/grant-permissions
Authorization: Bearer <admin_jwt_token>
Content-Type: application/json

{
  "admin_id": 2,
  "permissions": ["view_reports", "manage_compliance"]
}
```

---

### Notifications

#### Send Notification
```http
POST /api/admin/notifications/send
Authorization: Bearer <admin_jwt_token>
Content-Type: application/json

{
  "user_ids": [123, 456],
  "title": "Important Update",
  "message": "Please review your account",
  "type": "info"
}
```

---

## Error Responses

### Standard Error Format
```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {}
}
```

### Common HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created |
| 400 | Bad Request | Invalid input |
| 401 | Unauthorized | Missing or invalid token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource already exists |
| 500 | Internal Server Error | Server error |

---

## Rate Limiting

Currently no rate limiting implemented. Consider adding for production.

**Recommended limits:**
- Authentication endpoints: 5 requests/minute
- Read endpoints: 100 requests/minute
- Write endpoints: 30 requests/minute

---

## Pagination

List endpoints support pagination:

**Query Parameters:**
- `page` - Page number (default: 1)
- `per_page` - Items per page (default: 20, max: 100)

**Response includes:**
```json
{
  "data": [...],
  "total": 150,
  "page": 1,
  "per_page": 20,
  "total_pages": 8
}
```

---

## Filtering & Sorting

Many list endpoints support filtering and sorting:

**Query Parameters:**
- `search` - Search term
- `sort_by` - Field to sort by
- `sort_order` - `asc` or `desc`
- `status` - Filter by status
- `date_from` - Start date
- `date_to` - End date

**Example:**
```http
GET /api/admin/clients?search=john&sort_by=created_at&sort_order=desc&status=active
```

---

## Webhooks

Not currently implemented. Consider adding for:
- Payment notifications
- KYC status updates
- Document uploads
- Support ticket updates

---

## API Versioning

Current version: v1 (implicit)

Future versions will use URL versioning:
- v1: `/api/v1/...`
- v2: `/api/v2/...`

---

## Testing

### Postman Collection

Import the included Postman collection for easy testing:
- `QGI-Email-Tests.postman_collection.json`

### Example cURL Commands

**Test health endpoint:**
```bash
curl https://qgi-backend.onrender.com/api/health
```

**Login and save token:**
```bash
TOKEN=$(curl -X POST https://qgi-backend.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}' \
  | jq -r '.access_token')
```

**Use token in request:**
```bash
curl https://qgi-backend.onrender.com/api/investor/dashboard \
  -H "Authorization: Bearer $TOKEN"
```

---

**Last Updated:** November 4, 2025  
**API Version:** 1.0

