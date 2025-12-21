# Deployment Guide - UAV Security ML

## 🚀 Production Deployment Guide

This guide covers deploying the UAV Security ML application to production environments.

## Prerequisites

- Docker and Docker Compose installed
- PostgreSQL database (or use Docker Compose provided instance)
- Redis server (or use Docker Compose provided instance)
- SSL certificate (recommended for HTTPS)
- Domain name (optional but recommended)

---

## Quick Deployment with Docker Compose

The easiest way to deploy is using Docker Compose:

### 1. Clone Repository

```bash
git clone https://github.com/shivansh-12315646/uav_security_ml.git
cd uav_security_ml
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with production settings
nano .env
```

**Important Production Settings:**

```env
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-very-strong-secret-key-here-change-me
DEBUG=False

# Database (PostgreSQL for production)
DATABASE_URL=postgresql://uav_user:strong_password@db:5432/uav_security

# Redis
REDIS_URL=redis://redis:6379/0

# JWT
JWT_SECRET_KEY=your-jwt-secret-key-here

# Admin User
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=very-strong-password-here

# Email (for notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Security
BCRYPT_LOG_ROUNDS=12
RATE_LIMIT_PER_MINUTE=60
```

### 3. Generate Strong Secrets

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate JWT_SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Build and Start Services

```bash
# Build and start all services
docker-compose up -d --build

# Check logs
docker-compose logs -f app
```

### 5. Verify Deployment

```bash
# Check running containers
docker-compose ps

# Test application
curl http://localhost:5000/api/v1/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "UAV Security ML",
  "version": "2.0.0"
}
```

### 6. Access Application

- Application: `http://localhost:5000`
- Login with admin credentials from `.env`

---

## Cloud Platform Deployment

### AWS Deployment

#### Option 1: AWS Elastic Beanstalk

```bash
# Install EB CLI
pip install awsebcli

# Initialize EB
eb init -p docker uav-security-ml

# Create environment
eb create uav-security-production

# Deploy
eb deploy

# Open application
eb open
```

#### Option 2: AWS ECS with Fargate

1. **Build and Push Docker Image**

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

# Build image
docker build -t uav-security-ml .

# Tag image
docker tag uav-security-ml:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/uav-security-ml:latest

# Push image
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/uav-security-ml:latest
```

2. **Create ECS Task Definition**

```json
{
  "family": "uav-security-ml",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "app",
      "image": "YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/uav-security-ml:latest",
      "portMappings": [
        {
          "containerPort": 5000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "FLASK_ENV",
          "value": "production"
        },
        {
          "name": "DATABASE_URL",
          "value": "postgresql://user:pass@your-rds.amazonaws.com:5432/uav_security"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/uav-security-ml",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

3. **Create ECS Service**

Use AWS Console or CLI to create ECS service with load balancer.

---

### Google Cloud Platform (GCP)

#### Cloud Run Deployment

```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Build and submit
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/uav-security-ml

# Deploy
gcloud run deploy uav-security-ml \
  --image gcr.io/YOUR_PROJECT_ID/uav-security-ml \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars FLASK_ENV=production,DATABASE_URL=postgresql://... \
  --memory 2Gi \
  --cpu 2
```

---

### Heroku Deployment

```bash
# Login to Heroku
heroku login

# Create app
heroku create uav-security-ml

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Add Redis
heroku addons:create heroku-redis:hobby-dev

# Set environment variables
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
heroku config:set ADMIN_PASSWORD=your-strong-password

# Deploy
git push heroku main

# Open app
heroku open
```

---

### DigitalOcean App Platform

1. **Via DigitalOcean Console:**
   - Create new app
   - Connect GitHub repository
   - Select Dockerfile deployment
   - Configure environment variables
   - Deploy

2. **Via CLI:**

```bash
# Install doctl
brew install doctl  # or appropriate for your OS

# Authenticate
doctl auth init

# Create app
doctl apps create --spec .do/app.yaml

# Get app URL
doctl apps list
```

**.do/app.yaml:**
```yaml
name: uav-security-ml
services:
  - name: web
    dockerfile_path: Dockerfile
    github:
      repo: shivansh-12315646/uav_security_ml
      branch: main
      deploy_on_push: true
    envs:
      - key: FLASK_ENV
        value: production
      - key: SECRET_KEY
        type: SECRET
    instance_count: 1
    instance_size_slug: basic-xxs
    http_port: 5000
databases:
  - name: db
    engine: PG
    version: "14"
  - name: redis
    engine: REDIS
    version: "7"
```

---

## HTTPS Setup (SSL/TLS)

### Option 1: Nginx Reverse Proxy with Let's Encrypt

1. **Install Nginx and Certbot**

```bash
sudo apt update
sudo apt install nginx certbot python3-certbot-nginx
```

2. **Configure Nginx**

`/etc/nginx/sites-available/uav-security-ml`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

3. **Enable Site and Get Certificate**

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/uav-security-ml /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### Option 2: Traefik (Docker)

Add to `docker-compose.yml`:

```yaml
services:
  traefik:
    image: traefik:v2.10
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.myresolver.acme.tlschallenge=true"
      - "--certificatesresolvers.myresolver.acme.email=your-email@example.com"
      - "--certificatesresolvers.myresolver.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./letsencrypt:/letsencrypt

  app:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.app.rule=Host(`yourdomain.com`)"
      - "traefik.http.routers.app.entrypoints=websecure"
      - "traefik.http.routers.app.tls.certresolver=myresolver"
```

---

## Monitoring and Logging

### Application Monitoring

**Install monitoring tools:**

```bash
# Add to requirements.txt
prometheus-flask-exporter==0.22.3
```

**Configure in app:**

```python
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)
```

### Logging

**Configure production logging:**

```python
# config.py
import logging

if FLASK_ENV == 'production':
    logging.basicConfig(
        filename='logs/app.log',
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s'
    )
```

### Health Checks

The application includes a health check endpoint:

```bash
GET /api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "UAV Security ML",
  "version": "2.0.0"
}
```

---

## Database Backup

### PostgreSQL Backup

```bash
# Manual backup
docker-compose exec db pg_dump -U uav_user uav_security > backup.sql

# Automated backup (cron job)
0 2 * * * docker-compose -f /path/to/docker-compose.yml exec -T db pg_dump -U uav_user uav_security > /backups/uav_$(date +\%Y\%m\%d).sql
```

### Restore

```bash
docker-compose exec -T db psql -U uav_user uav_security < backup.sql
```

---

## Performance Optimization

### 1. Database Optimization

```sql
-- Add indexes for frequently queried fields
CREATE INDEX idx_detections_user_id ON detection_history(user_id);
CREATE INDEX idx_detections_created_at ON detection_history(created_at);
CREATE INDEX idx_alerts_status ON alerts(status);
```

### 2. Redis Caching

Already configured in the application. Ensure Redis is running.

### 3. Gunicorn Workers

Adjust based on your server:

```bash
# Formula: (2 x CPU cores) + 1
gunicorn --workers 9 --bind 0.0.0.0:5000 wsgi:app
```

### 4. Static File Serving

For production, use CDN or nginx for static files.

---

## Security Checklist

- [ ] Change all default passwords
- [ ] Use strong SECRET_KEY and JWT_SECRET_KEY
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall (UFW, security groups)
- [ ] Set up database backups
- [ ] Enable rate limiting
- [ ] Configure CORS properly
- [ ] Keep dependencies updated
- [ ] Monitor logs regularly
- [ ] Use environment variables for secrets
- [ ] Enable database connection pooling
- [ ] Set up intrusion detection

---

## Troubleshooting

### Application Won't Start

```bash
# Check logs
docker-compose logs app

# Check database connection
docker-compose exec app python -c "from app import create_app; app = create_app()"
```

### Database Connection Issues

```bash
# Verify database is running
docker-compose exec db psql -U uav_user -d uav_security -c "SELECT 1;"
```

### High Memory Usage

```bash
# Reduce Gunicorn workers
# Adjust in Dockerfile or docker-compose.yml
CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:5000", "wsgi:app"]
```

---

## Support

For issues and questions:
- GitHub Issues: https://github.com/shivansh-12315646/uav_security_ml/issues
- Email: shivanshsep16@gmail.com

---

## License

MIT License - See LICENSE file for details
