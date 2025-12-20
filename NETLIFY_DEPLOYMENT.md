# Netlify Deployment Guide - UAV Security ML

## 📋 Overview

This guide explains how to deploy the UAV Security ML project to Netlify. Since this is a full-stack Flask application with database requirements, the deployment uses a **hybrid architecture**:

- **Netlify**: Hosts static landing page, documentation, and serverless functions
- **Backend Service** (Render/Railway/Heroku): Hosts the complete Flask application

## 🏗️ Architecture

```
┌─────────────────┐
│   Netlify CDN   │  Static Assets, Landing Page
│  (Edge Network) │  Serverless Functions
└────────┬────────┘
         │
         │ (API Calls)
         │
┌────────▼────────┐
│  Backend Server │  Flask App, Database, ML Models
│ (Render/Railway)│  Real-time Features, Authentication
└─────────────────┘
```

## 🚀 Quick Deploy to Netlify

### Option 1: One-Click Deploy

[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start/deploy?repository=https://github.com/shivansh-12315646/uav_security_ml)

1. Click the button above
2. Connect your GitHub account
3. Authorize repository access
4. Netlify will:
   - Clone the repository
   - Read `netlify.toml` configuration
   - Run build command: `pip install -r requirements.txt && python build_static.py`
   - Deploy the `build/` directory
5. Your site will be live at `https://[random-name].netlify.app`

### Option 2: Manual Deploy via Dashboard

1. **Go to Netlify Dashboard**
   - Visit [https://app.netlify.com](https://app.netlify.com)
   - Click "Add new site" → "Import an existing project"

2. **Connect to Git Provider**
   - Select "GitHub"
   - Authorize Netlify
   - Choose `uav_security_ml` repository

3. **Configure Build Settings**
   - Netlify will auto-detect settings from `netlify.toml`
   - Verify settings:
     - **Build command**: `pip install -r requirements.txt && python build_static.py`
     - **Publish directory**: `build`
     - **Functions directory**: `netlify/functions`

4. **Deploy**
   - Click "Deploy site"
   - Wait for build to complete (~2-3 minutes)
   - Site will be live!

### Option 3: Netlify CLI

```bash
# Install Netlify CLI globally
npm install -g netlify-cli

# Login to Netlify
netlify login

# Initialize Netlify in project directory
cd /path/to/uav_security_ml
netlify init

# Follow prompts:
# - Create & configure a new site
# - Choose team
# - Site name: uav-security-ml (or your choice)

# Deploy to production
netlify deploy --prod

# Or deploy for preview
netlify deploy
```

### Option 4: Drag and Drop

```bash
# Build the static site locally
python build_static.py

# Go to https://app.netlify.com/drop
# Drag the 'build' folder to the drop zone
# Instant deployment!
```

## ⚙️ Configuration Files

### netlify.toml

The `netlify.toml` file contains all deployment configuration:

```toml
[build]
  command = "pip install -r requirements.txt && python build_static.py"
  publish = "build"
  functions = "netlify/functions"

[build.environment]
  PYTHON_VERSION = "3.10"
```

### build_static.py

This Python script generates the static site:
- Creates `build/` directory
- Generates `index.html` landing page
- Creates `404.html` error page
- Copies CSS and JS assets

### runtime.txt

Specifies Python version for Netlify:
```
3.10
```

## 🔧 Environment Variables

Set these in Netlify Dashboard → Site Settings → Environment Variables:

### Optional Variables

```bash
# Backend API URL (if deploying full app separately)
API_URL=https://your-backend-api.render.com

# For production
NODE_ENV=production
```

### How to Set Environment Variables

1. Go to Netlify Dashboard
2. Select your site
3. Click "Site settings"
4. Navigate to "Environment variables"
5. Click "Add a variable"
6. Enter key and value
7. Click "Save"

## 🧪 Testing the Deployment

### Test Endpoints

After deployment, test these URLs:

```bash
# Landing page
https://your-site.netlify.app/

# Health check serverless function
https://your-site.netlify.app/.netlify/functions/health

# Project info serverless function
https://your-site.netlify.app/.netlify/functions/info
```

### Using curl

```bash
# Test health endpoint
curl https://your-site.netlify.app/.netlify/functions/health

# Expected response:
# {
#   "status": "healthy",
#   "service": "UAV Security ML - Netlify Static Site",
#   "version": "1.0.0"
# }

# Test info endpoint
curl https://your-site.netlify.app/.netlify/functions/info
```

### Local Testing

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Test functions locally
netlify dev

# This starts:
# - Local dev server at http://localhost:8888
# - Functions at http://localhost:8888/.netlify/functions/
```

## 🌐 Custom Domain

### Add Custom Domain

1. **Go to Domain Settings**
   - Netlify Dashboard → Site → Domain settings
   - Click "Add custom domain"

2. **Enter Your Domain**
   - Example: `uav-security.yourdomain.com`
   - Click "Verify"

3. **Configure DNS**
   - **Option A: Netlify DNS (Recommended)**
     - Use Netlify nameservers
     - Automatic SSL provisioning
   
   - **Option B: External DNS**
     - Add CNAME record:
       ```
       CNAME  uav-security  [your-site].netlify.app
       ```

4. **SSL Certificate**
   - Automatically provisioned by Let's Encrypt
   - Usually ready in minutes
   - Auto-renewal enabled

### Domain Aliases

```bash
# Add domain via CLI
netlify domains:add yourdomain.com

# List domains
netlify domains:list
```

## 🔄 Continuous Deployment

### Automatic Deploys

Netlify automatically deploys when you push to GitHub:

```bash
# Make changes
git add .
git commit -m "Update landing page"
git push origin main

# Netlify automatically:
# 1. Detects the push
# 2. Runs build command
# 3. Deploys new version
# 4. Site live in ~2-3 minutes
```

### Deploy Contexts

- **Production**: Deploys from `main` branch
- **Deploy Previews**: Automatic previews for pull requests
- **Branch Deploys**: Deploy specific branches

Configure in `netlify.toml`:

```toml
[context.production]
  command = "python build_static.py"

[context.deploy-preview]
  command = "python build_static.py"

[context.branch-deploy]
  command = "python build_static.py"
```

### Deploy Hooks

Create webhook for external triggers:

1. Site Settings → Build & Deploy → Build hooks
2. Click "Add build hook"
3. Name it (e.g., "Rebuild site")
4. Select branch
5. Save and copy webhook URL

Trigger deploy:
```bash
curl -X POST -d {} https://api.netlify.com/build_hooks/YOUR_HOOK_ID
```

## 📊 Netlify Features

### Form Handling

Add to HTML:
```html
<form name="contact" method="POST" data-netlify="true">
  <input type="text" name="name" />
  <input type="email" name="email" />
  <textarea name="message"></textarea>
  <button type="submit">Send</button>
</form>
```

### Redirects and Rewrites

Already configured in `netlify.toml`:
```toml
[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### Analytics

Enable in Netlify Dashboard:
- Real-time visitor stats
- Pageviews
- Top pages
- Traffic sources

## 🔐 Security

### Headers

Security headers configured in `netlify.toml`:

```toml
[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-XSS-Protection = "1; mode=block"
    X-Content-Type-Options = "nosniff"
```

### HTTPS

- SSL certificate automatically provisioned
- All traffic forced to HTTPS
- HTTP/2 enabled by default

### Environment Variable Security

- Never commit secrets to Git
- Use Netlify environment variables
- Variables are encrypted at rest
- Not exposed in client-side code

## 🚢 Deploying Full Application

For complete functionality (database, ML models, authentication), deploy the Flask backend:

### Render (Recommended)

```bash
# Use the included render.yaml
# Or deploy via Render Dashboard
```

1. Go to [render.com](https://render.com)
2. Connect GitHub repository
3. Create new Web Service
4. Render auto-detects settings
5. Add environment variables
6. Deploy

### Railway

```bash
railway login
railway init
railway up
```

### Heroku

```bash
heroku create uav-security-ml
heroku addons:create heroku-postgresql:hobby-dev
heroku addons:create heroku-redis:hobby-dev
git push heroku main
```

### Connect Frontend to Backend

Update Netlify environment variable:
```bash
API_URL=https://your-backend.render.com
```

## 🐛 Troubleshooting

### Build Fails

**Error: Python not found**
```bash
# Solution: Ensure runtime.txt exists with version
echo "3.10" > runtime.txt
```

**Error: Module not found**
```bash
# Solution: Check requirements.txt includes all dependencies
pip freeze > requirements.txt
```

**Error: Build timeout**
```bash
# Solution: Reduce build time
# - Remove unnecessary dependencies
# - Use build cache
```

### Functions Not Working

**404 on function calls**
```bash
# Check:
# 1. Functions are in netlify/functions/
# 2. Function has handler(event, context)
# 3. Returns proper response format
```

**Function errors**
```bash
# View logs:
# Netlify Dashboard → Functions → Click function → Logs
```

### Deployment Issues

**Site not updating**
```bash
# Clear cache and redeploy
netlify deploy --prod --clear-cache

# Or in Dashboard:
# Deploys → Trigger deploy → Clear cache and deploy site
```

**Build succeeds but site broken**
```bash
# Check build logs
# Verify publish directory is correct
# Test build locally:
python build_static.py
cd build
python -m http.server 8000
```

### DNS Issues

**Domain not resolving**
```bash
# Check DNS propagation
dig yourdomain.com

# Can take up to 48 hours
# Use https://dnschecker.org to verify
```

## 📈 Monitoring

### Build Notifications

Configure in Site Settings → Build & Deploy → Deploy notifications:
- Email notifications
- Slack integration
- Webhook notifications
- GitHub commit status

### Analytics

Enable Netlify Analytics:
- $9/month per site
- Server-side analytics (no client script)
- GDPR compliant
- No cookie consent needed

### Logs

View logs:
```bash
# Via CLI
netlify logs

# Or in Dashboard:
# Site → Functions → Select function → Logs
```

## 💰 Pricing

### Netlify Free Tier

- 100 GB bandwidth/month
- 300 build minutes/month
- Unlimited sites
- Deploy previews
- Instant rollbacks
- Community support

Perfect for this project! ✅

### Upgrade if Needed

- **Pro**: $19/month - 400 GB bandwidth, 1000 build minutes
- **Business**: Custom pricing - Advanced features

## 🎓 Best Practices

1. **Version Control**
   - Always commit `netlify.toml`
   - Don't commit `build/` directory
   - Use `.gitignore` properly

2. **Environment Variables**
   - Never hardcode secrets
   - Use Netlify environment variables
   - Different values for dev/prod

3. **Build Optimization**
   - Minimize build time
   - Cache dependencies when possible
   - Use efficient build scripts

4. **Testing**
   - Test locally before deploying
   - Use deploy previews for PRs
   - Monitor build logs

5. **Security**
   - Keep dependencies updated
   - Use security headers
   - Enable HTTPS
   - Validate user input in functions

## 📚 Additional Resources

- [Netlify Documentation](https://docs.netlify.com)
- [Netlify Functions Guide](https://docs.netlify.com/functions/overview/)
- [Netlify CLI Reference](https://cli.netlify.com)
- [Project Repository](https://github.com/shivansh-12315646/uav_security_ml)
- [DEPLOYMENT.md](DEPLOYMENT.md) - Full deployment guide

## 🆘 Support

**Issues with Netlify deployment?**

1. Check [Netlify Support Forums](https://answers.netlify.com)
2. Review [build logs](#) in dashboard
3. Open issue on [GitHub](https://github.com/shivansh-12315646/uav_security_ml/issues)

**For full application deployment:**
- See [DEPLOYMENT.md](DEPLOYMENT.md)
- Check platform-specific guides (Render, Railway, Heroku)

---

**Last Updated**: December 2024  
**Version**: 1.0.0  
**Status**: Production Ready ✅
