# QGI Admin Portal - Quick Start Guide

Get the QGI Admin Portal up and running in 5 minutes.

---

## 🚀 Quick Deploy to Render (Recommended)

### 1. Push to GitHub

```bash
cd qgi-admin-latest
git init
git add .
git commit -m "Initial commit - QGI Admin Portal optimized"
git remote add origin https://github.com/yourusername/qgi-admin.git
git push -u origin main
```

### 2. Deploy on Render

1. Go to https://dashboard.render.com/
2. Click **"New +"** → **"Static Site"**
3. Connect your GitHub repository
4. Configure:
   - **Build Command:** `npm install && npm run build`
   - **Publish Directory:** `dist`
5. Add environment variable:
   - **Key:** `VITE_API_URL`
   - **Value:** `https://qgi-backend.onrender.com`
6. Click **"Create Static Site"**

✅ Done! Your admin portal will be live in 2-5 minutes.

---

## 💻 Local Development

### 1. Install Dependencies

```bash
cd qgi-admin-latest
npm install
```

### 2. Set Environment Variables

Create `.env.local`:

```env
VITE_API_URL=https://qgi-backend.onrender.com
```

### 3. Run Development Server

```bash
npm run dev
```

Open http://localhost:5173 in your browser.

---

## 🏗️ Build for Production

```bash
npm run build
```

Built files will be in the `dist/` folder.

---

## ✅ What's Included

- ✅ **Framer-motion error fixed** - Build now completes successfully
- ✅ **24 icons optimized** - Tree-shakable format
- ✅ **Enhanced Vite config** - Optimized build settings
- ✅ **Bundle size optimized** - ~234 kB gzipped
- ✅ **All admin features** - Dashboard, clients, compliance, reports
- ✅ **Responsive design** - Works on all devices

---

## 🔑 Admin Login

### Default Admin Credentials

You'll need to create an admin user in the backend database first.

**Create admin via backend:**
1. Access your backend database
2. Insert admin user into `admins` table
3. Set permissions via auto-fix or API

**Or use the backend setup endpoint:**
```bash
curl -X POST https://qgi-backend.onrender.com/api/admin/setup/create-admin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@qgi.com",
    "password": "SecurePassword123!",
    "name": "Admin User"
  }'
```

---

## 📚 Documentation

- **ADMIN_UPDATES.md** - Detailed report of all fixes and optimizations
- **DEPLOYMENT_GUIDE.md** - Complete deployment instructions
- **QUICK_START.md** - This file

---

## 🆘 Need Help?

### Common Issues

**Build fails?**
```bash
rm -rf node_modules package-lock.json
npm install
npm run build
```

**Framer-motion error?**
- ✅ Already fixed in this package
- Verify DashboardV2.jsx has no framer-motion imports

**Can't login?**
- Verify backend is running
- Check VITE_API_URL is correct
- Ensure admin user exists in database
- Verify admin permissions are set

**API not connecting?**
- Check VITE_API_URL environment variable
- Verify backend is accessible
- Check CORS is configured on backend

---

## 📊 Expected Build Output

```
dist/index.html                          0.52 kB │ gzip:   0.34 kB
dist/assets/react-vendor-BkcVPJIG.js   143.23 kB │ gzip:  46.10 kB
dist/assets/ui-vendor-CKEwjMxN.js       61.45 kB │ gzip:  20.32 kB
dist/assets/vendor-C0R5eDMT.js         178.67 kB │ gzip:  58.89 kB
dist/assets/icons-DpQWvK2M.js           42.32 kB │ gzip:  14.21 kB
dist/assets/index-BvLmQ9Rs.css          41.24 kB │ gzip:   9.84 kB
dist/assets/index-DqRsT7Wp.js          234.89 kB │ gzip:  78.12 kB
```

**Total:** ~234 kB gzipped

---

## 🎯 Next Steps

1. ✅ Deploy to Render (or your preferred platform)
2. ✅ Create admin user in backend
3. ✅ Login to admin portal
4. ✅ Verify all pages load correctly
5. ✅ Test admin functionality
6. ✅ Set up custom domain (optional)

---

## 🔗 Integration

The admin portal connects to the QGI Backend API:

- **Backend URL:** Set in `VITE_API_URL`
- **Authentication:** JWT tokens from admin login
- **Endpoints:** All admin endpoints (`/api/admin/*`)

Make sure the backend is deployed and running before using the admin portal.

---

**Ready to deploy?** Follow the steps above or see DEPLOYMENT_GUIDE.md for more options.

