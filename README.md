# UAV Security with Machine Learning

[![Netlify Status](https://api.netlify.com/api/v1/badges/your-site-id/deploy-status)](https://app.netlify.com/sites/your-site-name/deploys)
[![Python Version](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Advanced Machine Learning System for UAV Threat Detection and Security Analysis**

## Modernized Features

UAV Security with Machine Learning is packed with premium-grade features, including:
- **UI Animations:** Smooth and intuitive animations for enhanced user experience.
- **Graphical Analytics:** State-of-the-art graphical representation of data.
- **Real-Time Training Monitoring:** Keep track of your training in real-time.
- **Model Comparison:** Compare different models seamlessly to achieve the best outcomes.

---

## Quick Start

### Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/shivansh-12315646/uav_security_ml.git
   cd uav_security_ml
   ```

2. **Set up environment:**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env with your settings
   nano .env
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize database:**
   ```bash
   # The database will be created automatically on first run
   # Default admin credentials are in .env file
   ```

5. **Run the application:**
   ```bash
   # Full-featured application with authentication
   python run.py
   
   # Or use with gunicorn for production
   gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
   ```

6. **Access the application:**
   - Open your browser to `http://localhost:5000`
   - Login with admin credentials from `.env`

### Build Static Site for Netlify

```bash
# Generate static landing page
python build_static.py

# Preview build output
cd build
python -m http.server 8000
```

---

## Premium Showcase

Explore the most compelling aspects of this project:
- **Real-Time Dashboard:** Monitor and track data and metrics in real time.
- **Interactive Visualizations:** Dynamic visual exploration of datasets and models.
- **Application Highlights:** Integrated features designed for premium usability and performance.

---

## Deployment Options

Deploy UAV Security ML on your preferred platform:

### 🌐 Netlify (Static Landing Page)

Deploy the static landing page and documentation to Netlify:

[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start/deploy?repository=https://github.com/shivansh-12315646/uav_security_ml)

**Quick Deploy:**
1. Click the "Deploy to Netlify" button above
2. Connect your GitHub account
3. Configure build settings (pre-configured in `netlify.toml`)
4. Deploy!

**Manual Deployment:**
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Deploy
netlify deploy --prod
```

**Note:** The Netlify deployment hosts a static landing page. For full backend functionality (database, ML models, real-time features), deploy the Flask application to one of the platforms below.

### 🚀 Render (Recommended for Full App)

```bash
# Use render.yaml for one-click deployment
# Or deploy via Render Dashboard
```

### 🚂 Railway

```bash
railway login
railway init
railway up
```

### 🟣 Heroku

```bash
heroku create uav-security-ml
heroku addons:create heroku-postgresql:hobby-dev
heroku addons:create heroku-redis:hobby-dev
git push heroku main
```

### 🐳 Docker

```bash
docker-compose up -d --build
```

**Live Demos:**
- **Static Site (Netlify):** [Will be available after deployment]
- **Full Application:** [Deploy to Render/Railway for full features]

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)

---

## Training Guide Refinement

Step-by-step instructions for leveraging the training dashboard and analytics:
1. Launch the training dashboard:
   ```bash
   python training_dashboard.py
   ```
2. Upload your dataset via the dashboard interface.
3. Start the training process by selecting the desired model and configuration.
4. Use the **Interactive Analytics** tab to visualize real-time metrics and analyze results.
5. Compare models using the **Model Comparison** feature to refine your choice.

Enjoy a modernized and user-friendly experience as you dive into UAV security with machine learning!

---

## 🌐 Netlify Deployment Guide

### Architecture Overview

The UAV Security ML project uses a hybrid deployment architecture:

- **Netlify**: Hosts the static landing page, documentation, and serverless functions
- **Backend Platform** (Render/Railway/Heroku): Hosts the full Flask application with database and ML features

### Netlify Configuration

The repository includes pre-configured Netlify deployment files:

- **`netlify.toml`**: Build configuration and settings
- **`build_static.py`**: Static site generator
- **`netlify/functions/`**: Serverless functions for API endpoints
- **`runtime.txt`**: Python runtime version

### Deployment Steps

#### Option 1: One-Click Deploy

1. Click the "Deploy to Netlify" button in the Deployment section
2. Authorize Netlify to access your GitHub repository
3. Netlify will automatically:
   - Read `netlify.toml` configuration
   - Run `python build_static.py` to generate static assets
   - Deploy the `build/` directory
   - Set up serverless functions

#### Option 2: Netlify CLI

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Initialize project (first time only)
netlify init

# Deploy to production
netlify deploy --prod

# Or deploy for testing
netlify deploy
```

#### Option 3: GitHub Integration

1. Push your code to GitHub
2. Go to [Netlify Dashboard](https://app.netlify.com)
3. Click "New site from Git"
4. Select your repository
5. Netlify auto-detects settings from `netlify.toml`
6. Click "Deploy site"

### Environment Variables

Set these in Netlify Dashboard → Site Settings → Environment Variables:

```bash
# Optional: Backend API URL if deploying full app separately
API_URL=https://your-backend-api.render.com

# Python version (handled by runtime.txt)
PYTHON_VERSION=3.10
```

### Testing the Deployment

After deployment, test these endpoints:

```bash
# Landing page
https://your-site.netlify.app/

# Health check function
https://your-site.netlify.app/.netlify/functions/health

# Project info function
https://your-site.netlify.app/.netlify/functions/info
```

### Full Application Deployment

For complete functionality including:
- User authentication and database
- Real-time ML model training
- WebSocket support for live updates
- Alert management system
- Analytics dashboard

Deploy the Flask backend to:

**Render (Recommended):**
```bash
# Use the pre-configured render.yaml
# Or deploy via Render Dashboard
```

**Railway:**
```bash
railway login
railway init
railway up
```

**Heroku:**
```bash
heroku create uav-security-ml
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
```

Then update the Netlify environment variable:
```bash
API_URL=https://your-backend.render.com
```

### Hybrid Deployment Benefits

- **Fast Global CDN**: Static assets served via Netlify's CDN
- **Serverless Functions**: Lightweight API endpoints without managing servers
- **Scalable Backend**: Full Flask app on dedicated platform with database
- **Cost-Effective**: Free Netlify tier for static site + affordable backend hosting
- **Easy Updates**: Git push triggers automatic redeployment

### Troubleshooting

**Build fails:**
```bash
# Check build logs in Netlify dashboard
# Ensure Python 3.10 is specified in runtime.txt
# Verify all dependencies in requirements.txt
```

**Functions not working:**
```bash
# Check function logs in Netlify dashboard
# Ensure functions are in netlify/functions/ directory
# Verify handler function signature
```

**Static site not updating:**
```bash
# Clear deploy cache in Netlify dashboard
# Trigger manual deploy
netlify deploy --prod --clear-cache
```

### Custom Domain

1. Go to Netlify Dashboard → Domain Settings
2. Add your custom domain
3. Configure DNS settings as instructed
4. SSL certificate is automatically provisioned

### Monitoring

- **Netlify Analytics**: Available in site dashboard
- **Function Logs**: Real-time logs for serverless functions
- **Deploy Notifications**: Configure Slack/email alerts
- **Build Hooks**: Trigger rebuilds via webhooks

---