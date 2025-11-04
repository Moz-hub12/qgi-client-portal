# QGI Client Portal - Deployment Guide

This guide provides step-by-step instructions for deploying the optimized QGI Client Portal to various hosting platforms.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Deployment to Render.com (Recommended)](#deployment-to-rendercom-recommended)
3. [Deployment to Vercel](#deployment-to-vercel)
4. [Deployment to Netlify](#deployment-to-netlify)
5. [Manual Deployment](#manual-deployment)
6. [Environment Variables](#environment-variables)
7. [Post-Deployment Verification](#post-deployment-verification)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before deploying, ensure you have:

- ✅ Node.js 18+ installed
- ✅ Git installed and configured
- ✅ GitHub account (for Render/Vercel/Netlify)
- ✅ Backend API URL (e.g., `https://qgi-backend.onrender.com`)
- ✅ All optimizations applied (see OPTIMIZATION_REPORT.md)

---

## Deployment to Render.com (Recommended)

Render.com offers free static site hosting with automatic deployments from GitHub.

### Step 1: Push to GitHub

```bash
# Navigate to the project directory
cd qgi-client-portal-latest

# Initialize git (if not already initialized)
git init

# Add all files
git add .

# Commit changes
git commit -m "QGI Client Portal - Optimized version with all fixes"

# Add remote repository (replace with your repo URL)
git remote add origin https://github.com/yourusername/qgi-frontend.git

# Push to GitHub
git push -u origin main
```

### Step 2: Create New Static Site on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Static Site"**
3. Connect your GitHub repository
4. Configure the site:
   - **Name:** `qgi-client-portal`
   - **Branch:** `main`
   - **Build Command:** `npm install && npm run build`
   - **Publish Directory:** `dist`

### Step 3: Add Environment Variables

In the Render dashboard, add the following environment variable:

| Key | Value |
|-----|-------|
| `VITE_API_URL` | `https://qgi-backend.onrender.com` |

### Step 4: Deploy

1. Click **"Create Static Site"**
2. Render will automatically build and deploy your site
3. Wait for the build to complete (usually 2-5 minutes)
4. Your site will be available at `https://qgi-client-portal.onrender.com`

### Step 5: Custom Domain (Optional)

1. In Render dashboard, go to your static site
2. Click **"Settings"** → **"Custom Domain"**
3. Add your custom domain (e.g., `app.qgi.com`)
4. Follow DNS configuration instructions

---

## Deployment to Vercel

Vercel offers excellent performance and automatic deployments.

### Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

### Step 2: Deploy

```bash
# Navigate to project directory
cd qgi-client-portal-latest

# Login to Vercel
vercel login

# Deploy
vercel

# Follow the prompts:
# - Set up and deploy? Yes
# - Which scope? Your account
# - Link to existing project? No
# - Project name? qgi-client-portal
# - Directory? ./
# - Override settings? No
```

### Step 3: Add Environment Variables

```bash
# Add environment variable
vercel env add VITE_API_URL

# Enter value when prompted:
# https://qgi-backend.onrender.com

# Select environments: Production, Preview, Development
```

### Step 4: Deploy to Production

```bash
vercel --prod
```

Your site will be available at `https://qgi-client-portal.vercel.app`

---

## Deployment to Netlify

Netlify offers drag-and-drop deployment and automatic builds from Git.

### Method 1: Drag and Drop (Quick)

1. Build the project locally:
   ```bash
   cd qgi-client-portal-latest
   npm install
   npm run build
   ```

2. Go to [Netlify Drop](https://app.netlify.com/drop)
3. Drag the `dist/` folder onto the page
4. Your site will be deployed instantly

### Method 2: Git Integration (Recommended)

1. Push your code to GitHub (see Render Step 1)
2. Go to [Netlify Dashboard](https://app.netlify.com/)
3. Click **"Add new site"** → **"Import an existing project"**
4. Connect to GitHub and select your repository
5. Configure build settings:
   - **Build Command:** `npm run build`
   - **Publish Directory:** `dist`
6. Add environment variable:
   - **Key:** `VITE_API_URL`
   - **Value:** `https://qgi-backend.onrender.com`
7. Click **"Deploy site"**

Your site will be available at `https://random-name.netlify.app`

### Custom Domain on Netlify

1. Go to **"Site settings"** → **"Domain management"**
2. Click **"Add custom domain"**
3. Follow DNS configuration instructions

---

## Manual Deployment

For deploying to your own server or hosting provider.

### Step 1: Build the Project

```bash
cd qgi-client-portal-latest
npm install
npm run build
```

### Step 2: Configure Environment Variables

Create a `.env.production` file:

```env
VITE_API_URL=https://qgi-backend.onrender.com
```

Rebuild with production environment:

```bash
npm run build
```

### Step 3: Upload Files

Upload the contents of the `dist/` folder to your web server:

- **Apache:** Upload to `/var/www/html/` or your document root
- **Nginx:** Upload to `/usr/share/nginx/html/` or your configured root
- **IIS:** Upload to `C:\inetpub\wwwroot\` or your site root

### Step 4: Configure Server

#### Apache (.htaccess)

Create `.htaccess` in the root directory:

```apache
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /
  RewriteRule ^index\.html$ - [L]
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d
  RewriteRule . /index.html [L]
</IfModule>
```

#### Nginx

Add to your nginx configuration:

```nginx
location / {
  try_files $uri $uri/ /index.html;
}
```

#### IIS (web.config)

Create `web.config` in the root directory:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>
    <rewrite>
      <rules>
        <rule name="React Routes" stopProcessing="true">
          <match url=".*" />
          <conditions logicalGrouping="MatchAll">
            <add input="{REQUEST_FILENAME}" matchType="IsFile" negate="true" />
            <add input="{REQUEST_FILENAME}" matchType="IsDirectory" negate="true" />
          </conditions>
          <action type="Rewrite" url="/" />
        </rule>
      </rules>
    </rewrite>
  </system.webServer>
</configuration>
```

---

## Environment Variables

The application requires the following environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API base URL | `https://qgi-backend.onrender.com` |

### Setting Environment Variables

#### During Build (Recommended)

Create `.env.production`:

```env
VITE_API_URL=https://qgi-backend.onrender.com
```

#### In Hosting Platform

- **Render:** Dashboard → Environment → Add Environment Variable
- **Vercel:** `vercel env add VITE_API_URL`
- **Netlify:** Site settings → Build & deploy → Environment → Add variable

---

## Post-Deployment Verification

After deployment, verify the following:

### 1. Build Verification

Check the build output for:
- ✅ No errors or warnings
- ✅ Bundle sizes are optimized (~267 kB gzipped)
- ✅ All chunks generated correctly

### 2. Functionality Testing

Test the following features:

- [ ] **Login Page**
  - Page loads without errors
  - Can enter credentials
  - Login redirects to dashboard

- [ ] **Dashboard**
  - Loads without crashes
  - Portfolio data displays
  - Charts render correctly
  - Recent transactions table shows data

- [ ] **Documents Page**
  - Lists all documents
  - Can download documents
  - Upload functionality works

- [ ] **Profile Page**
  - User information displays
  - Can update profile
  - Password change works

- [ ] **Support Page**
  - Can view support tickets
  - Can create new tickets
  - File attachments work

- [ ] **Announcements Page**
  - Lists all announcements
  - Can view announcement details

### 3. Performance Testing

Use browser DevTools to verify:

- [ ] **Network Tab**
  - Initial load < 2 seconds (on good connection)
  - Chunked assets load correctly
  - No failed requests

- [ ] **Console Tab**
  - No JavaScript errors
  - No React warnings

- [ ] **Lighthouse Score**
  - Performance > 90
  - Accessibility > 90
  - Best Practices > 90

### 4. Cross-Browser Testing

Test on:
- [ ] Chrome/Edge (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Mobile browsers (iOS Safari, Chrome Mobile)

---

## Troubleshooting

### Build Fails with "Cannot find module"

**Solution:** Ensure all dependencies are installed:
```bash
rm -rf node_modules package-lock.json
npm install
npm run build
```

### "404 Not Found" on Page Refresh

**Problem:** Server not configured for SPA routing.

**Solution:** Add server configuration for SPA routing (see Manual Deployment → Configure Server)

### Environment Variables Not Working

**Problem:** Environment variables not set correctly.

**Solution:**
1. Ensure variables are prefixed with `VITE_`
2. Rebuild after adding variables: `npm run build`
3. Check variables are set in hosting platform

### Large Bundle Size

**Problem:** Bundle size increased after changes.

**Solution:**
1. Verify all icon imports use tree-shakable format
2. Check no large libraries added
3. Run build and check output sizes
4. Compare with expected sizes in OPTIMIZATION_REPORT.md

### API Requests Failing

**Problem:** Frontend can't connect to backend.

**Solution:**
1. Verify `VITE_API_URL` is set correctly
2. Check backend is deployed and running
3. Verify CORS is configured on backend
4. Check network tab for actual API URL being called

### Charts Not Rendering

**Problem:** Recharts not loading correctly.

**Solution:**
1. Verify Recharts is in main bundle (not chunked separately)
2. Check vite.config.js doesn't have Recharts in manualChunks
3. Clear browser cache and reload

---

## Continuous Deployment

### Automatic Deployments from GitHub

All major platforms support automatic deployments:

**Render:**
- Automatically deploys on push to `main` branch
- Configure in Dashboard → Settings → Build & Deploy

**Vercel:**
- Automatically deploys on push to any branch
- Production deployments on push to `main`
- Preview deployments on pull requests

**Netlify:**
- Automatically deploys on push to configured branch
- Deploy previews on pull requests

### Manual Deployments

To trigger manual deployment:

**Render:**
- Dashboard → Manual Deploy → Deploy latest commit

**Vercel:**
```bash
vercel --prod
```

**Netlify:**
```bash
netlify deploy --prod
```

---

## Rollback Procedure

If deployment fails or causes issues:

### Render
1. Go to Dashboard → Deploys
2. Find previous successful deployment
3. Click **"Redeploy"**

### Vercel
```bash
# List deployments
vercel ls

# Rollback to specific deployment
vercel rollback [deployment-url]
```

### Netlify
1. Go to Deploys tab
2. Find previous successful deployment
3. Click **"Publish deploy"**

---

## Security Considerations

### Environment Variables
- ✅ Never commit `.env` files to Git
- ✅ Use platform-specific environment variable management
- ✅ Rotate API keys regularly

### HTTPS
- ✅ Always use HTTPS in production
- ✅ Enable HSTS headers
- ✅ Configure CSP headers

### API Security
- ✅ Ensure backend has CORS configured correctly
- ✅ Use authentication tokens (JWT)
- ✅ Implement rate limiting on backend

---

## Performance Optimization Tips

### CDN Configuration
- Enable CDN on hosting platform for faster global access
- Configure cache headers for static assets

### Compression
- Enable Brotli compression (most platforms enable by default)
- Verify gzip fallback is available

### Monitoring
- Set up uptime monitoring (UptimeRobot, Pingdom)
- Configure error tracking (Sentry, LogRocket)
- Monitor performance metrics (Google Analytics, Plausible)

---

## Support

For deployment issues:
1. Check this guide's troubleshooting section
2. Review platform-specific documentation
3. Check platform status pages
4. Contact platform support if needed

For application issues:
1. Check OPTIMIZATION_REPORT.md
2. Review browser console for errors
3. Verify backend API is accessible
4. Check environment variables are set correctly

---

## Quick Reference

### Common Commands

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run tests (if configured)
npm test
```

### Important Files

- `vite.config.js` - Build configuration
- `package.json` - Dependencies and scripts
- `.env.production` - Production environment variables
- `dist/` - Built files for deployment

### Important URLs

- **Render Dashboard:** https://dashboard.render.com/
- **Vercel Dashboard:** https://vercel.com/dashboard
- **Netlify Dashboard:** https://app.netlify.com/

---

**Last Updated:** November 4, 2025  
**Version:** 1.0 (Optimized)

