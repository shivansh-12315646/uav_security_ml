"""
Build script for generating static assets for Netlify deployment.
This creates a static landing page and documentation site for the UAV Security ML project.
"""
import os
import shutil
from pathlib import Path

def create_build_directory():
    """Create the build directory structure."""
    build_dir = Path('build')
    
    # Remove existing build directory
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    # Create new build directory
    build_dir.mkdir(exist_ok=True)
    (build_dir / 'css').mkdir(exist_ok=True)
    (build_dir / 'js').mkdir(exist_ok=True)
    (build_dir / 'images').mkdir(exist_ok=True)
    
    return build_dir

def copy_static_assets(build_dir):
    """Copy static assets to build directory."""
    static_dir = Path('static')
    
    if static_dir.exists():
        # Copy CSS files
        css_dir = static_dir / 'css'
        if css_dir.exists():
            for css_file in css_dir.glob('*.css'):
                shutil.copy2(css_file, build_dir / 'css')
        
        # Copy JS files
        js_dir = static_dir / 'js'
        if js_dir.exists():
            for js_file in js_dir.glob('*.js'):
                shutil.copy2(js_file, build_dir / 'js')
    
    print("✓ Static assets copied")

def create_landing_page(build_dir):
    """Create a static landing page."""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="UAV Security with Machine Learning - Advanced threat detection for unmanned aerial vehicles">
    <title>UAV Security ML - Advanced UAV Threat Detection</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        header {
            text-align: center;
            color: white;
            padding: 4rem 0 2rem;
        }
        
        h1 {
            font-size: 3rem;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        
        .tagline {
            font-size: 1.5rem;
            opacity: 0.9;
            margin-bottom: 2rem;
        }
        
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin: 3rem 0;
        }
        
        .feature-card {
            background: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s ease;
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
        }
        
        .feature-card h3 {
            color: #667eea;
            margin-bottom: 1rem;
            font-size: 1.5rem;
        }
        
        .feature-card p {
            color: #666;
            line-height: 1.8;
        }
        
        .cta-section {
            background: white;
            padding: 3rem;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin: 3rem 0;
            text-align: center;
        }
        
        .cta-section h2 {
            color: #667eea;
            margin-bottom: 1.5rem;
            font-size: 2rem;
        }
        
        .button-group {
            display: flex;
            gap: 1rem;
            justify-content: center;
            flex-wrap: wrap;
            margin-top: 2rem;
        }
        
        .btn {
            display: inline-block;
            padding: 1rem 2rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s ease;
            font-size: 1rem;
        }
        
        .btn-primary {
            background: #667eea;
            color: white;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn-primary:hover {
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }
        
        .btn-secondary {
            background: white;
            color: #667eea;
            border: 2px solid #667eea;
        }
        
        .btn-secondary:hover {
            background: #f0f4ff;
        }
        
        .deployment-info {
            background: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin: 2rem 0;
        }
        
        .deployment-info h2 {
            color: #667eea;
            margin-bottom: 1rem;
        }
        
        .deployment-info code {
            background: #f5f5f5;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            color: #e83e8c;
        }
        
        .deployment-info pre {
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 1rem;
            border-radius: 8px;
            overflow-x: auto;
            margin: 1rem 0;
        }
        
        .tech-stack {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            justify-content: center;
            margin: 2rem 0;
        }
        
        .tech-badge {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-weight: 600;
            backdrop-filter: blur(10px);
        }
        
        footer {
            text-align: center;
            color: white;
            padding: 2rem 0;
            margin-top: 3rem;
        }
        
        .icon {
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🛡️ UAV Security ML</h1>
            <p class="tagline">Advanced Machine Learning for UAV Threat Detection</p>
            <div class="tech-stack">
                <span class="tech-badge">🐍 Python</span>
                <span class="tech-badge">⚡ Flask</span>
                <span class="tech-badge">🤖 Machine Learning</span>
                <span class="tech-badge">📊 Real-time Analytics</span>
                <span class="tech-badge">🔒 Security First</span>
            </div>
        </header>
        
        <div class="features">
            <div class="feature-card">
                <div class="icon">🎯</div>
                <h3>Real-Time Detection</h3>
                <p>Advanced machine learning models analyze UAV behavior patterns in real-time to detect potential security threats with high accuracy.</p>
            </div>
            
            <div class="feature-card">
                <div class="icon">📊</div>
                <h3>Interactive Analytics</h3>
                <p>Comprehensive dashboard with real-time visualizations, historical data analysis, and predictive insights for proactive security.</p>
            </div>
            
            <div class="feature-card">
                <div class="icon">🔔</div>
                <h3>Smart Alerts</h3>
                <p>Intelligent alert system with severity classification, customizable notifications, and automated threat response protocols.</p>
            </div>
            
            <div class="feature-card">
                <div class="icon">🧠</div>
                <h3>ML Model Training</h3>
                <p>Train and compare multiple machine learning models including Random Forest, XGBoost, and Neural Networks with live monitoring.</p>
            </div>
            
            <div class="feature-card">
                <div class="icon">👥</div>
                <h3>User Management</h3>
                <p>Role-based access control, user authentication, and comprehensive admin panel for team collaboration and security.</p>
            </div>
            
            <div class="feature-card">
                <div class="icon">📈</div>
                <h3>Performance Metrics</h3>
                <p>Detailed model performance metrics, confusion matrices, ROC curves, and feature importance analysis for optimization.</p>
            </div>
        </div>
        
        <div class="cta-section">
            <h2>Get Started with UAV Security ML</h2>
            <p>Deploy the full-featured application on your preferred platform</p>
            <div class="button-group">
                <a href="https://github.com/shivansh-12315646/uav_security_ml" class="btn btn-primary" target="_blank">
                    📦 View on GitHub
                </a>
                <a href="#deployment" class="btn btn-secondary">
                    🚀 Deployment Guide
                </a>
                <a href="#documentation" class="btn btn-secondary">
                    📚 Documentation
                </a>
            </div>
        </div>
        
        <div class="deployment-info" id="deployment">
            <h2>🚀 Deployment Options</h2>
            <p>This is a full-stack Flask application with database and real-time features. Choose your deployment platform:</p>
            
            <h3 style="margin-top: 2rem; color: #667eea;">Option 1: Render (Recommended)</h3>
            <pre>git clone https://github.com/shivansh-12315646/uav_security_ml.git
cd uav_security_ml
# Follow DEPLOYMENT.md for Render setup</pre>
            
            <h3 style="margin-top: 2rem; color: #667eea;">Option 2: Railway</h3>
            <pre># One-click deploy with Railway
railway up</pre>
            
            <h3 style="margin-top: 2rem; color: #667eea;">Option 3: Heroku</h3>
            <pre>heroku create uav-security-ml
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main</pre>
            
            <h3 style="margin-top: 2rem; color: #667eea;">Option 4: Docker</h3>
            <pre>docker-compose up -d --build</pre>
            
            <h3 style="margin-top: 2rem; color: #667eea;">Local Development</h3>
            <pre>pip install -r requirements.txt
python run.py</pre>
            
            <p style="margin-top: 2rem; padding: 1rem; background: #fff3cd; border-radius: 8px; color: #856404;">
                <strong>Note:</strong> This Netlify deployment hosts the static landing page. For the full application with backend functionality, 
                deploy to Render, Railway, Heroku, or use Docker. See <code>DEPLOYMENT.md</code> for detailed instructions.
            </p>
        </div>
        
        <div class="deployment-info" id="documentation">
            <h2>📚 Key Features</h2>
            <ul style="margin-left: 2rem; line-height: 2;">
                <li><strong>User Authentication:</strong> Secure login with role-based access control</li>
                <li><strong>Real-time Dashboard:</strong> Live monitoring of UAV security metrics</li>
                <li><strong>ML Model Training:</strong> Train and compare multiple models</li>
                <li><strong>Alert Management:</strong> Customizable alerts with severity levels</li>
                <li><strong>Data Analytics:</strong> Comprehensive analytics and reporting</li>
                <li><strong>API Endpoints:</strong> RESTful API for integration</li>
                <li><strong>WebSocket Support:</strong> Real-time updates via SocketIO</li>
                <li><strong>Database Support:</strong> PostgreSQL for production, SQLite for development</li>
            </ul>
            
            <h3 style="margin-top: 2rem; color: #667eea;">Tech Stack</h3>
            <ul style="margin-left: 2rem; line-height: 2;">
                <li><strong>Backend:</strong> Flask, SQLAlchemy, Flask-SocketIO</li>
                <li><strong>ML Libraries:</strong> scikit-learn, XGBoost, SHAP, pandas, numpy</li>
                <li><strong>Database:</strong> PostgreSQL (production), SQLite (development)</li>
                <li><strong>Caching:</strong> Redis</li>
                <li><strong>Security:</strong> Flask-Login, Flask-JWT-Extended, Flask-Bcrypt</li>
                <li><strong>Testing:</strong> pytest, pytest-flask</li>
            </ul>
        </div>
        
        <footer>
            <p>&copy; 2024 UAV Security ML Project. Open Source MIT License.</p>
            <p style="margin-top: 0.5rem; opacity: 0.8;">
                <a href="https://github.com/shivansh-12315646/uav_security_ml" style="color: white; text-decoration: none;">
                    GitHub Repository
                </a>
            </p>
        </footer>
    </div>
</body>
</html>"""
    
    with open(build_dir / 'index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✓ Landing page created")

def create_404_page(build_dir):
    """Create a 404 error page."""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>404 - Page Not Found | UAV Security ML</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            text-align: center;
            padding: 2rem;
        }
        .container {
            max-width: 600px;
        }
        h1 {
            font-size: 6rem;
            margin-bottom: 1rem;
        }
        h2 {
            font-size: 2rem;
            margin-bottom: 1rem;
        }
        p {
            font-size: 1.2rem;
            margin-bottom: 2rem;
            opacity: 0.9;
        }
        a {
            display: inline-block;
            padding: 1rem 2rem;
            background: white;
            color: #667eea;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            transition: transform 0.3s ease;
        }
        a:hover {
            transform: translateY(-2px);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>404</h1>
        <h2>Page Not Found</h2>
        <p>The page you're looking for doesn't exist or has been moved.</p>
        <a href="/">← Back to Home</a>
    </div>
</body>
</html>"""
    
    with open(build_dir / '404.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✓ 404 page created")

def main():
    """Main build process."""
    try:
        print("🏗️  Building static site for Netlify...")
        print()
        
        build_dir = create_build_directory()
        copy_static_assets(build_dir)
        create_landing_page(build_dir)
        create_404_page(build_dir)
        
        print()
        print("✅ Build complete! Static site ready in 'build/' directory")
        print("📁 Files:")
        for file in build_dir.rglob('*'):
            if file.is_file():
                print(f"   - {file.relative_to(build_dir)}")
        
        return 0
    
    except PermissionError as e:
        print(f"❌ Permission error: {e}")
        print("   Make sure you have write permissions to the current directory.")
        return 1
    
    except OSError as e:
        print(f"❌ File system error: {e}")
        print("   Check disk space and file permissions.")
        return 1
    
    except Exception as e:
        print(f"❌ Unexpected error during build: {e}")
        print("   Please check the error message and try again.")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    exit(main())
