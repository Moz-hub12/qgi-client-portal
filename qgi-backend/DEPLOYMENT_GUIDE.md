# QGI Backend - Deployment Guide

Complete deployment instructions for the QGI Backend API.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Deployment to Render (Recommended)](#deployment-to-render-recommended)
3. [Environment Variables](#environment-variables)
4. [Database Setup](#database-setup)
5. [Post-Deployment Verification](#post-deployment-verification)
6. [Troubleshooting](#troubleshooting)
7. [Maintenance](#maintenance)

---

## Prerequisites

Before deploying, ensure you have:

- ✅ GitHub account
- ✅ Render account (free tier works)
- ✅ PostgreSQL database (Render provides free tier)
- ✅ Supabase account (for file storage)
- ✅ SMTP email credentials (Gmail, SendGrid, etc.)
- ✅ All code pushed to GitHub repository

---

## Deployment to Render (Recommended)

Render offers free tier with auto-deploy from GitHub, perfect for this backend.

### Step 1: Create PostgreSQL Database

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"PostgreSQL"**
3. Configure database:
   - **Name:** `qgi-database`
   - **Database:** `qgi_db`
   - **User:** `qgi_user`
   - **Region:** Choose closest to your users
   - **Plan:** Free (or paid for production)
4. Click **"Create Database"**
5. **Copy the Internal Database URL** (starts with `postgresql://`)

### Step 2: Push Code to GitHub

```bash
cd qgi-backend-latest

# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "QGI Backend - Production ready with all updates"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/yourusername/qgi-backend.git

# Push to GitHub
git push -u origin main
```

### Step 3: Create Web Service on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure the service:
   - **Name:** `qgi-backend`
   - **Region:** Same as database
   - **Branch:** `main`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn src.main:app --bind 0.0.0.0:$PORT`

### Step 4: Add Environment Variables

In the Render dashboard, add the following environment variables:

| Key | Value | Notes |
|-----|-------|-------|
| `DATABASE_URL` | `<internal_database_url>` | From Step 1 |
| `JWT_SECRET_KEY` | `<random_secret_key>` | Generate strong key |
| `SUPABASE_URL` | `https://xxx.supabase.co` | From Supabase dashboard |
| `SUPABASE_KEY` | `eyJxxx...` | Service role key from Supabase |
| `MAIL_SERVER` | `smtp.gmail.com` | Your SMTP server |
| `MAIL_PORT` | `587` | SMTP port (587 for TLS) |
| `MAIL_USERNAME` | `noreply@qgi.com` | Your email |
| `MAIL_PASSWORD` | `<app_password>` | Email password/app password |
| `MAIL_USE_TLS` | `True` | Enable TLS |
| `MAIL_USE_SSL` | `False` | Disable SSL (using TLS) |
| `FRONTEND_URL` | `https://qgi-frontend.onrender.com` | Client portal URL |
| `ADMIN_FRONTEND_URL` | `https://qgi-admin.onrender.com` | Admin dashboard URL |
| `PYTHON_VERSION` | `3.11.0` | Python version |

**Generate JWT Secret Key:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Step 5: Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone your repository
   - Install dependencies
   - Start the application
3. Wait for deployment (usually 2-5 minutes)
4. Your backend will be available at `https://qgi-backend.onrender.com`

---

## Environment Variables

### Required Variables

#### Database
- **DATABASE_URL** - PostgreSQL connection string
  - Format: `postgresql://user:password@host:port/database`
  - Get from Render PostgreSQL service (use Internal URL)

#### Authentication
- **JWT_SECRET_KEY** - Secret key for JWT token signing
  - Generate: `python3 -c "import secrets; print(secrets.token_hex(32))"`
  - Keep this secret and secure

#### Supabase (File Storage)
- **SUPABASE_URL** - Your Supabase project URL
  - Get from: Supabase Dashboard → Settings → API
- **SUPABASE_KEY** - Service role key (not anon key)
  - Get from: Supabase Dashboard → Settings → API → Service Role Key

#### Email (SMTP)
- **MAIL_SERVER** - SMTP server address
  - Gmail: `smtp.gmail.com`
  - SendGrid: `smtp.sendgrid.net`
- **MAIL_PORT** - SMTP port
  - TLS: `587`
  - SSL: `465`
- **MAIL_USERNAME** - Email address or username
- **MAIL_PASSWORD** - Email password or app password
  - For Gmail: Use [App Password](https://support.google.com/accounts/answer/185833)
- **MAIL_USE_TLS** - Enable TLS (recommended)
  - Value: `True`
- **MAIL_USE_SSL** - Enable SSL
  - Value: `False` (if using TLS)

#### CORS (Frontend URLs)
- **FRONTEND_URL** - Client portal URL
  - Example: `https://qgi-frontend.onrender.com`
  - Used for CORS and email links
- **ADMIN_FRONTEND_URL** - Admin dashboard URL
  - Example: `https://qgi-admin.onrender.com`
  - Used for CORS

### Optional Variables

- **FLASK_ENV** - Environment mode
  - Development: `development`
  - Production: `production` (default)
- **LOG_LEVEL** - Logging level
  - Options: `DEBUG`, `INFO`, `WARNING`, `ERROR`
  - Default: `INFO`

---

## Database Setup

### Automatic Table Creation

The backend automatically creates all required tables on first startup using SQLAlchemy's `db.create_all()`.

**Tables Created:**
- `users` - Client user accounts
- `investor_data` - Client investment data
- `admins` - Admin user accounts
- `admin_sessions` - Admin login sessions
- `documents` - Document metadata
- `announcements` - Company announcements
- `support_requests` - Support tickets
- `support_messages` - Support ticket messages
- `magic_link_tokens` - Passwordless login tokens

### Manual Database Access (If Needed)

If you need to access the database directly:

1. Go to Render Dashboard → PostgreSQL service
2. Click **"Connect"** → **"External Connection"**
3. Use provided credentials with psql or pgAdmin

**Example psql connection:**
```bash
psql -h <host> -U <user> -d <database>
```

### Database Migrations

For schema changes:
1. Update models in `src/models/`
2. Test locally with fresh database
3. Deploy to Render (tables auto-update)

**Note:** For production, consider using Flask-Migrate for proper migrations.

---

## Post-Deployment Verification

### 1. Check Deployment Status

In Render dashboard:
- ✅ Build completed successfully
- ✅ Service is "Live"
- ✅ No errors in logs

### 2. Test Health Endpoint

```bash
curl https://qgi-backend.onrender.com/api/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-04T12:00:00Z"
}
```

### 3. Verify Auto-Fix Permissions

Check Render logs for:
```
Auto-fix admin permissions completed
```

If you see this, permissions are set correctly.

### 4. Test Client Endpoints

#### Register User
```bash
curl -X POST https://qgi-backend.onrender.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!",
    "name": "Test User"
  }'
```

#### Login
```bash
curl -X POST https://qgi-backend.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'
```

**Expected:** JWT token in response

### 5. Test Admin Endpoints

#### Admin Login
```bash
curl -X POST https://qgi-backend.onrender.com/api/admin/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@qgi.com",
    "password": "admin_password"
  }'
```

#### Get Dashboard Stats (with token)
```bash
curl https://qgi-backend.onrender.com/api/admin/reports/dashboard-stats \
  -H "Authorization: Bearer <admin_jwt_token>"
```

### 6. Test Database Connection

Check Render logs for:
```
Database connection successful
Tables created/verified
```

---

## Troubleshooting

### Build Fails

**Problem:** Dependencies won't install

**Solution:**
```bash
# Verify requirements.txt is correct
cat requirements.txt

# Test locally
pip install -r requirements.txt
```

### Service Won't Start

**Problem:** Application crashes on startup

**Solutions:**
1. Check Render logs for error messages
2. Verify all environment variables are set
3. Check DATABASE_URL is correct (use Internal URL)
4. Ensure PYTHON_VERSION is set to 3.11.0

### Database Connection Errors

**Problem:** Can't connect to database

**Solutions:**
1. Use **Internal Database URL** (not External)
2. Verify database service is running
3. Check database and web service are in same region
4. Ensure DATABASE_URL includes all parameters

### Mapper Configuration Errors

**Problem:** SQLAlchemy mapper errors in logs

**Solution:**
- ✅ Already fixed in this package
- All models use shared `db` instance from `user.py`
- If you add new models, import `db` from `user.py`

### Permission Errors

**Problem:** Admin can't access certain endpoints

**Solutions:**
1. Check auto-fix ran on startup (check logs)
2. Manually fix via API:
   ```bash
   curl -X POST https://qgi-backend.onrender.com/api/admin/setup/fix-permissions \
     -H "Authorization: Bearer <admin_jwt_token>"
   ```
3. Check admin exists in database
4. Verify JWT token is valid

### CORS Errors

**Problem:** Frontend can't access backend

**Solutions:**
1. Set `FRONTEND_URL` and `ADMIN_FRONTEND_URL` correctly
2. Include protocol (`https://`)
3. Don't include trailing slash
4. Restart service after changing environment variables

### Email Not Sending

**Problem:** Email functionality not working

**Solutions:**
1. Verify SMTP credentials are correct
2. For Gmail, use App Password (not regular password)
3. Check MAIL_PORT matches TLS/SSL setting
4. Test SMTP connection separately
5. Check Render logs for email errors

### Slow Response Times

**Problem:** API responses are slow

**Solutions:**
1. Upgrade from free tier (free tier sleeps after inactivity)
2. Use paid tier for always-on service
3. Optimize database queries
4. Add database indexes
5. Consider caching for frequently accessed data

---

## Maintenance

### Viewing Logs

1. Go to Render Dashboard
2. Click on your web service
3. Click **"Logs"** tab
4. View real-time logs

**Filter logs:**
- Click filter icon
- Select log level (INFO, WARNING, ERROR)

### Restarting Service

1. Go to Render Dashboard
2. Click on your web service
3. Click **"Manual Deploy"** → **"Clear build cache & deploy"**

### Updating Code

Render auto-deploys on git push:

```bash
# Make changes
git add .
git commit -m "Update description"
git push

# Render automatically deploys
```

### Database Backups

Render PostgreSQL includes automatic backups on paid plans.

**Manual backup:**
```bash
pg_dump -h <host> -U <user> -d <database> > backup.sql
```

### Monitoring

**Set up monitoring:**
1. Use Render's built-in metrics
2. Set up UptimeRobot for uptime monitoring
3. Configure error tracking (Sentry, Rollbar)
4. Monitor database performance

**Key Metrics:**
- Response times
- Error rates
- Database connections
- Memory usage
- Request volume

### Scaling

**Free Tier Limitations:**
- Sleeps after 15 minutes of inactivity
- 750 hours/month free
- Shared resources

**Upgrade to Paid:**
1. Go to Render Dashboard
2. Click on service
3. Click **"Upgrade"**
4. Choose plan (Starter: $7/month)

**Benefits:**
- Always on (no sleep)
- More resources
- Better performance
- Database backups

---

## Security Best Practices

### Environment Variables
- ✅ Never commit `.env` files to git
- ✅ Use strong, random JWT_SECRET_KEY
- ✅ Rotate secrets regularly
- ✅ Use Render's environment variable management

### Database
- ✅ Use Internal Database URL (not External)
- ✅ Enable SSL for database connections (Render default)
- ✅ Regular backups
- ✅ Monitor for suspicious activity

### API Security
- ✅ JWT authentication on all protected endpoints
- ✅ CORS configured for specific origins
- ✅ Input validation on all endpoints
- ✅ Rate limiting (consider adding)
- ✅ HTTPS only (Render default)

### Admin Access
- ✅ Strong admin passwords
- ✅ Permission-based access control
- ✅ Session management
- ✅ Audit logging (consider adding)

---

## Performance Optimization

### Database
- Add indexes on frequently queried columns
- Use connection pooling
- Optimize queries (avoid N+1 problems)
- Consider read replicas for scaling

### Caching
- Add Redis for session storage
- Cache frequently accessed data
- Use ETags for API responses

### Code
- Use async operations where possible
- Optimize database queries
- Minimize external API calls
- Profile slow endpoints

---

## Quick Reference

### Common Commands

```bash
# View logs
render logs <service-name>

# Deploy manually
render deploy <service-name>

# Run migrations (if using Flask-Migrate)
flask db upgrade

# Test endpoint
curl https://qgi-backend.onrender.com/api/health
```

### Important URLs

- **Render Dashboard:** https://dashboard.render.com/
- **Backend URL:** https://qgi-backend.onrender.com
- **Database:** Render Dashboard → PostgreSQL service
- **Logs:** Render Dashboard → Web Service → Logs

### Support Resources

- **Render Docs:** https://render.com/docs
- **Flask Docs:** https://flask.palletsprojects.com/
- **SQLAlchemy Docs:** https://docs.sqlalchemy.org/

---

**Last Updated:** November 4, 2025  
**Version:** 1.0 (Production Ready)

