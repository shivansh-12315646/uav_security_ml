# 🚀 Quick Start - Netlify Deployment

## One-Click Deploy

The fastest way to deploy the UAV Security ML landing page:

[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start/deploy?repository=https://github.com/shivansh-12315646/uav_security_ml)

**Just click the button above!** Netlify will:
1. Clone the repository
2. Build the static site using `build_static.py`
3. Deploy to a live URL
4. Provide a unique Netlify subdomain

**Your site will be live in ~2 minutes!** ⚡

---

## What Gets Deployed?

The Netlify deployment creates a **static landing page** with:

- 🎨 Beautiful, responsive design
- 📱 Mobile-friendly interface
- 📊 Project feature showcase
- 📚 Deployment documentation
- 🔌 Serverless API endpoints (`/api/health`, `/api/info`)
- 🔒 Security headers
- ⚡ Global CDN distribution

---

## For Full Application Features

The static site is perfect for showcasing the project. For the **full application** with:
- 🗄️ Database (PostgreSQL)
- 🔐 User authentication
- 🤖 ML model training
- 📊 Real-time analytics dashboard
- 🔔 Alert management
- 📡 WebSocket support

Deploy the Flask backend to:

### Recommended Platform: Render

```bash
# See DEPLOYMENT.md for complete instructions
```

1. Visit [render.com](https://render.com)
2. Connect your GitHub repository
3. Use the included `render.yaml` configuration
4. Add environment variables from `.env.example`
5. Deploy!

### Alternative Platforms

- **Railway**: `railway up`
- **Heroku**: See `DEPLOYMENT.md`
- **Docker**: `docker-compose up -d`

---

## Environment Setup (Optional)

For the static Netlify site, no environment variables are required!

If you're connecting to a backend API:

1. Go to Netlify Dashboard
2. Site Settings → Environment Variables
3. Add: `API_URL=https://your-backend.render.com`

---

## Local Testing

Want to test before deploying?

```bash
# Generate the static site
python build_static.py

# Preview it
cd build
python -m http.server 8000

# Visit http://localhost:8000
```

---

## Files & Structure

```
uav_security_ml/
├── netlify.toml              # Netlify configuration
├── build_static.py           # Static site generator
├── runtime.txt               # Python version (3.10)
├── netlify/
│   └── functions/            # Serverless functions
│       ├── health.py         # Health check endpoint
│       └── info.py           # Project info endpoint
├── build/                    # Generated static site (gitignored)
│   ├── index.html
│   ├── 404.html
│   ├── css/
│   └── js/
└── static/                   # Source assets
    ├── css/
    └── js/
```

---

## Next Steps After Deployment

1. ✅ **Verify deployment**: Visit your Netlify URL
2. 🎨 **Custom domain** (optional): Add in Netlify dashboard
3. 📊 **Enable analytics** (optional): Netlify Analytics available
4. 🔗 **Update README**: Add your actual Netlify URL
5. 🚀 **Deploy backend**: For full features (see above)

---

## Need Help?

- 📖 **Detailed Guide**: See [NETLIFY_DEPLOYMENT.md](NETLIFY_DEPLOYMENT.md)
- 🔧 **Full Deployment**: See [DEPLOYMENT.md](DEPLOYMENT.md)
- ✅ **Testing**: See [NETLIFY_TESTING_CHECKLIST.md](NETLIFY_TESTING_CHECKLIST.md)
- 🐛 **Issues**: Open an issue on GitHub

---

## Documentation

- [README.md](README.md) - Project overview
- [NETLIFY_DEPLOYMENT.md](NETLIFY_DEPLOYMENT.md) - Complete Netlify guide
- [DEPLOYMENT.md](DEPLOYMENT.md) - Full application deployment
- [NETLIFY_TESTING_CHECKLIST.md](NETLIFY_TESTING_CHECKLIST.md) - Testing guide

---

**Happy Deploying!** 🎉

*Built with ❤️ for UAV Security*
