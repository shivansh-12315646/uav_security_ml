# 🚀 Deploy to Netlify - Quick Guide

## ✨ One-Click Deploy

Click the button below to deploy to Netlify instantly:

[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start/deploy?repository=https://github.com/shivansh-12315646/uav_security_ml)

That's it! Netlify will automatically:
- ✅ Clone your repository
- ✅ Install dependencies
- ✅ Build the static site
- ✅ Deploy to a live URL

---

## 📋 What Gets Deployed

**Netlify Deployment Includes:**
- ✅ Static landing page with project information
- ✅ Serverless functions (health check, info endpoints)
- ✅ Documentation and feature showcase
- ✅ Fast global CDN delivery
- ✅ Automatic SSL certificate

**Note:** This is a **static landing page**. For the full application with:
- Database and authentication
- ML model training
- Real-time detection
- Alert management

Deploy the Flask backend to **Render**, **Railway**, or **Heroku** (see below).

---

## 🎯 Alternative: CLI Deploy

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Deploy (from project directory)
netlify deploy --prod
```

---

## 🔧 Configuration

All configuration is pre-configured in `netlify.toml`:
- Build command: `python build_static.py`
- Publish directory: `build/`
- Functions: `netlify/functions/`
- Python version: 3.10

---

## 🌐 Full Application Deployment

For complete functionality, deploy the backend separately:

### Option 1: Render (Recommended)
```bash
# Use render.yaml for one-click deploy
# Or deploy via Render Dashboard
```

### Option 2: Railway
```bash
railway login
railway up
```

### Option 3: Heroku
```bash
heroku create uav-security-ml
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
```

### Option 4: Docker
```bash
docker-compose up -d --build
```

Then update your Netlify environment variable to connect:
```
API_URL=https://your-backend.render.com
```

---

## ✅ Verify Deployment

After deployment, test these URLs:

- **Landing Page**: `https://your-site.netlify.app/`
- **Health Check**: `https://your-site.netlify.app/.netlify/functions/health`
- **Info Function**: `https://your-site.netlify.app/.netlify/functions/info`

---

## 📚 More Information

- Full deployment guide: [NETLIFY_DEPLOYMENT.md](NETLIFY_DEPLOYMENT.md)
- Backend setup: [DEPLOYMENT.md](DEPLOYMENT.md)
- Quick start: [QUICKSTART_NETLIFY.md](QUICKSTART_NETLIFY.md)

---

**Need help?** Check the [GitHub Issues](https://github.com/shivansh-12315646/uav_security_ml/issues)
