# UAV Security ML - Deployment Architecture

## Hybrid Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        End Users / Browsers                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTPS
                         │
         ┌───────────────▼────────────────┐
         │                                │
         │      Netlify Global CDN        │
         │  (Edge Network - 195+ POPs)    │
         │                                │
         │  • Static Landing Page         │
         │  • Documentation               │
         │  • Serverless Functions        │
         │  • SSL/TLS Automatic           │
         │  • DDoS Protection             │
         │                                │
         └───────────────┬────────────────┘
                         │
         ┌───────────────▼────────────────┐
         │                                │
         │    Netlify Build Pipeline      │
         │                                │
         │  1. Git Push Detected          │
         │  2. Run: python build_static.py│
         │  3. Generate build/ directory  │
         │  4. Deploy to Edge Network     │
         │  5. Invalidate Cache           │
         │                                │
         └────────────────────────────────┘


═══════════════════════════════════════════════════════════════════
                    For Full Application Features
═══════════════════════════════════════════════════════════════════

         ┌────────────────────────────────┐
         │                                │
         │    Backend Platform            │
         │  (Render / Railway / Heroku)   │
         │                                │
         │  • Flask Application           │
         │  • User Authentication         │
         │  • ML Model Training           │
         │  • Real-time Analytics         │
         │  • WebSocket Support           │
         │  • API Endpoints               │
         │                                │
         └───────────┬────────────────────┘
                     │
         ┌───────────▼────────────────────┐
         │                                │
         │    PostgreSQL Database         │
         │  (Managed Service)             │
         │                                │
         │  • User Data                   │
         │  • Detection History           │
         │  • ML Models Metadata          │
         │  • Alerts & Logs               │
         │                                │
         └────────────────────────────────┘

         ┌────────────────────────────────┐
         │                                │
         │    Redis Cache                 │
         │  (Managed Service)             │
         │                                │
         │  • Session Storage             │
         │  • Rate Limiting               │
         │  • SocketIO Messages           │
         │  • Celery Task Queue           │
         │                                │
         └────────────────────────────────┘
```

## Deployment Options Comparison

### Option 1: Netlify Only (Static Site)

**What you get:**
- ✅ Static landing page
- ✅ Project documentation
- ✅ Serverless functions (health, info endpoints)
- ✅ Global CDN
- ✅ Free SSL
- ✅ Automatic deployments

**What you don't get:**
- ❌ User authentication
- ❌ Database operations
- ❌ ML model training
- ❌ Real-time dashboard
- ❌ Alert management

**Best for:**
- Project showcase
- Documentation
- Demo/Preview
- Landing page

**Cost:** FREE (Netlify Starter)

---

### Option 2: Hybrid (Netlify + Backend)

**Architecture:**
```
Netlify (Static) ←→ Backend API (Render/Railway) ←→ Database + Redis
```

**What you get:**
- ✅ Everything from Option 1
- ✅ Full application features
- ✅ Database persistence
- ✅ ML model training
- ✅ User authentication
- ✅ Real-time updates
- ✅ API integration

**Best for:**
- Production deployment
- Full feature set
- Scalable solution

**Cost:**
- Netlify: FREE
- Backend: $7-25/month (Render/Railway/Heroku starter)
- Database: Included or $5-10/month
- Redis: Included or $5/month

---

### Option 3: Full Platform (Render/Railway/Heroku)

**Architecture:**
```
Platform (Web Service) ←→ Database ←→ Redis
```

**What you get:**
- ✅ Complete application
- ✅ All features
- ✅ Single platform management
- ✅ Integrated monitoring

**Best for:**
- Simplified deployment
- Single platform preference
- Enterprise use

**Cost:** $7-25/month (includes database)

---

## File Flow - Static Build Process

```
┌─────────────────────┐
│   Source Files      │
├─────────────────────┤
│ • static/css/*.css  │
│ • static/js/*.js    │
│ • app/templates/*   │
└──────────┬──────────┘
           │
           │ python build_static.py
           │
           ▼
┌─────────────────────┐
│  Build Process      │
├─────────────────────┤
│ 1. Create build/    │
│ 2. Generate HTML    │
│ 3. Copy CSS/JS      │
│ 4. Create 404 page  │
└──────────┬──────────┘
           │
           │ Output
           │
           ▼
┌─────────────────────┐
│  build/ Directory   │
├─────────────────────┤
│ • index.html        │
│ • 404.html          │
│ • css/*.css         │
│ • js/*.js           │
└──────────┬──────────┘
           │
           │ Netlify Deploy
           │
           ▼
┌─────────────────────┐
│  Netlify CDN        │
│  (195+ Locations)   │
└─────────────────────┘
```

## Request Flow - Netlify Deployment

```
User Browser
    │
    │ 1. Request https://your-site.netlify.app/
    ▼
Netlify Edge
    │
    │ 2. Serve index.html from nearest CDN location
    ▼
User Browser
    │
    │ 3. Load CSS/JS assets (cached at edge)
    ▼
Page Rendered
    │
    │ 4. Optional: API call to /.netlify/functions/health
    ▼
Netlify Function (Serverless)
    │
    │ 5. Execute Python function
    │ 6. Return JSON response
    ▼
User Browser
    │
    │ 7. Display data
    ▼
Complete!
```

## Request Flow - Full Application (with Backend)

```
User Browser
    │
    │ 1. Request https://your-site.netlify.app/
    ▼
Netlify Edge
    │
    │ 2. Serve static landing page
    ▼
User Browser
    │
    │ 3. Click "Login" or "Dashboard"
    │ 4. API Request to https://backend.render.com/api/login
    ▼
Backend Server (Render)
    │
    │ 5. Authenticate user
    ├─→ Check PostgreSQL database
    │ 6. Create session in Redis
    │ 7. Return JWT token
    ▼
User Browser
    │
    │ 8. Store token
    │ 9. Request dashboard data
    ▼
Backend Server
    │
    │ 10. Verify token
    │ 11. Query database for user data
    │ 12. Run ML predictions
    │ 13. Return JSON response
    ▼
User Browser
    │
    │ 14. Render dashboard
    │ 15. Establish WebSocket for real-time updates
    ▼
Complete!
```

## CI/CD Pipeline

```
Developer
    │
    │ git push origin main
    ▼
GitHub Repository
    │
    ├──────────────────────┬──────────────────────┐
    │                      │                      │
    ▼                      ▼                      ▼
Netlify                Render                 Heroku
    │                      │                      │
    │ Webhook              │ Webhook              │ Git Push
    ▼                      ▼                      ▼
Build                  Build                  Build
    │                      │                      │
    │ build_static.py      │ pip install          │ pip install
    │                      │ gunicorn start       │ Procfile
    ▼                      ▼                      ▼
Deploy                 Deploy                 Deploy
    │                      │                      │
    │ Edge Network         │ Web Service          │ Dyno
    ▼                      ▼                      ▼
Live Site              Live Backend           Live App
```

---

## Technology Stack

### Frontend (Netlify Static)
```
HTML5
  ├── Responsive Design
  ├── Semantic Markup
  └── SEO Optimized

CSS3
  ├── Modern Flexbox/Grid
  ├── Animations
  └── Mobile-First

JavaScript
  ├── Vanilla JS (No Framework)
  ├── Chart.js (if needed)
  └── Modern ES6+
```

### Backend (Full App)
```
Flask 3.0
  ├── SQLAlchemy (ORM)
  ├── Flask-Login (Auth)
  ├── Flask-SocketIO (Real-time)
  ├── Flask-WTF (Forms)
  └── Flask-CORS (API)

Machine Learning
  ├── scikit-learn
  ├── XGBoost
  ├── pandas
  ├── numpy
  └── SHAP

Infrastructure
  ├── PostgreSQL (Database)
  ├── Redis (Cache/Queue)
  ├── Gunicorn (WSGI Server)
  └── Nginx (Reverse Proxy)
```

---

## Security Layers

```
┌─────────────────────────────────────────┐
│          DDoS Protection                │  ← Netlify/Platform
├─────────────────────────────────────────┤
│          SSL/TLS Encryption             │  ← Let's Encrypt
├─────────────────────────────────────────┤
│          Security Headers               │  ← netlify.toml
├─────────────────────────────────────────┤
│          Rate Limiting                  │  ← Flask-Limiter
├─────────────────────────────────────────┤
│          CSRF Protection                │  ← Flask-WTF
├─────────────────────────────────────────┤
│          Authentication                 │  ← Flask-Login
├─────────────────────────────────────────┤
│          Authorization (RBAC)           │  ← Custom Logic
├─────────────────────────────────────────┤
│          Input Validation               │  ← WTForms
├─────────────────────────────────────────┤
│          SQL Injection Prevention       │  ← SQLAlchemy ORM
└─────────────────────────────────────────┘
```

---

## Scaling Strategy

### Horizontal Scaling
```
Load Balancer
    │
    ├─── App Server 1
    ├─── App Server 2
    ├─── App Server 3
    └─── App Server N
         │
         ├─── Database (Primary)
         │      └─── Replicas
         │
         └─── Redis Cluster
```

### Vertical Scaling
```
Basic:     1 CPU,  512 MB RAM  →  10-50 users
Standard:  2 CPU,  2 GB RAM    →  100-500 users
Premium:   4 CPU,  8 GB RAM    →  1000+ users
```

---

**Last Updated**: December 2024  
**Version**: 2.0.0
