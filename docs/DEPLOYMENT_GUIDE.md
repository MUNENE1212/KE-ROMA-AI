# KE-ROUMA Deployment Guide

## Overview

This guide covers deploying KE-ROUMA to production environments, including backend API deployment, frontend hosting, database setup, and monitoring configuration.

## Prerequisites

- Python 3.8+
- Node.js 16+
- MongoDB Atlas account
- OpenAI API key
- IntaSend account (for M-Pesa payments)
- Domain name and SSL certificate

## Environment Setup

### 1. Production Environment Variables

Create a `.env` file with production values:

```env
# Database
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/kerouma?retryWrites=true&w=majority
DATABASE_NAME=kerouma_prod

# OpenAI API
OPENAI_API_KEY=sk-your-production-openai-key

# IntaSend Payment Gateway
INTASEND_PUBLISHABLE_KEY=your_production_publishable_key
INTASEND_SECRET_KEY=your_production_secret_key
INTASEND_BASE_URL=https://payment.intasend.com/api/v1

# Security
SECRET_KEY=your-super-secure-secret-key-for-production
JWT_SECRET_KEY=your-jwt-secret-key
DEBUG=false

# App Settings
ENVIRONMENT=production
PREMIUM_PRICE=100
CORS_ORIGINS=["https://yourdomain.com", "https://www.yourdomain.com"]

# Monitoring
SENTRY_DSN=your-sentry-dsn-for-error-tracking
LOG_LEVEL=INFO
```

### 2. Security Configuration

```python
# config/production.py
import os
from typing import List

class ProductionConfig:
    DEBUG = False
    TESTING = False
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "https://yourdomain.com",
        "https://www.yourdomain.com"
    ]
    
    # Rate Limiting
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_PER_MINUTE = 60
    
    # SSL
    FORCE_HTTPS = True
    SECURE_COOKIES = True
```

## Backend Deployment Options

### Option 1: Google Cloud Run (Recommended)

#### 1. Prepare for Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `.dockerignore`:
```
.env
.env.local
.git
.gitignore
__pycache__
*.pyc
*.pyo
*.pyd
.pytest_cache
.coverage
.venv
venv/
mobile-app/
docs/
*.md
```

#### 2. Build and Deploy

```bash
# Install Google Cloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init

# Set project
gcloud config set project your-project-id

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Deploy to Cloud Run
gcloud run deploy kerouma-api \
    --source . \
    --platform managed \
    --region africa-south1 \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 10 \
    --port 8000 \
    --set-env-vars ENVIRONMENT=production
```

#### 3. Configure Custom Domain

```bash
# Map custom domain
gcloud run domain-mappings create \
    --service kerouma-api \
    --domain api.yourdomain.com \
    --region africa-south1
```

### Option 2: Heroku

#### 1. Prepare for Heroku

Create `Procfile`:
```
web: uvicorn app:app --host 0.0.0.0 --port $PORT
```

Create `runtime.txt`:
```
python-3.9.18
```

#### 2. Deploy to Heroku

```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login and create app
heroku login
heroku create kerouma-api

# Set environment variables
heroku config:set MONGODB_URL="your-mongodb-url"
heroku config:set OPENAI_API_KEY="your-openai-key"
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set ENVIRONMENT="production"

# Deploy
git push heroku main
```

### Option 3: DigitalOcean App Platform

Create `app.yaml`:
```yaml
name: kerouma-api
services:
- name: api
  source_dir: /
  github:
    repo: your-username/kerouma
    branch: main
  run_command: uvicorn app:app --host 0.0.0.0 --port 8080
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  http_port: 8080
  health_check:
    http_path: /health
  envs:
  - key: ENVIRONMENT
    value: production
  - key: MONGODB_URL
    value: your-mongodb-url
    type: SECRET
  - key: OPENAI_API_KEY
    value: your-openai-key
    type: SECRET
```

## Frontend Deployment Options

### Option 1: Netlify (Recommended for Static Sites)

#### 1. Build Configuration

Create `netlify.toml`:
```toml
[build]
  publish = "static"
  command = "echo 'Static site - no build needed'"

[build.environment]
  NODE_VERSION = "16"

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-XSS-Protection = "1; mode=block"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"
    Content-Security-Policy = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https://api.yourdomain.com"

[[redirects]]
  from = "/api/*"
  to = "https://api.yourdomain.com/api/:splat"
  status = 200
  force = true

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

#### 2. Deploy to Netlify

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login and deploy
netlify login
netlify init
netlify deploy --prod --dir=static
```

### Option 2: Vercel

Create `vercel.json`:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "static/**/*",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "https://api.yourdomain.com/api/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/static/$1"
    }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        }
      ]
    }
  ]
}
```

### Option 3: AWS S3 + CloudFront

#### 1. S3 Bucket Setup

```bash
# Create S3 bucket
aws s3 mb s3://kerouma-frontend

# Configure bucket for static website hosting
aws s3 website s3://kerouma-frontend \
    --index-document index.html \
    --error-document index.html

# Upload files
aws s3 sync static/ s3://kerouma-frontend --delete
```

#### 2. CloudFront Distribution

```json
{
  "CallerReference": "kerouma-frontend-2024",
  "Comment": "KE-ROUMA Frontend Distribution",
  "DefaultCacheBehavior": {
    "TargetOriginId": "S3-kerouma-frontend",
    "ViewerProtocolPolicy": "redirect-to-https",
    "MinTTL": 0,
    "ForwardedValues": {
      "QueryString": false,
      "Cookies": {
        "Forward": "none"
      }
    }
  },
  "Origins": {
    "Quantity": 1,
    "Items": [
      {
        "Id": "S3-kerouma-frontend",
        "DomainName": "kerouma-frontend.s3.amazonaws.com",
        "S3OriginConfig": {
          "OriginAccessIdentity": ""
        }
      }
    ]
  },
  "Enabled": true,
  "PriceClass": "PriceClass_100"
}
```

## Database Setup

### MongoDB Atlas Configuration

#### 1. Create Production Cluster

```bash
# Using MongoDB Atlas CLI
atlas clusters create production-cluster \
    --provider AWS \
    --region AF_SOUTH_1 \
    --tier M10 \
    --diskSizeGB 10 \
    --backup
```

#### 2. Security Configuration

```javascript
// Database user creation
db.createUser({
  user: "kerouma_app",
  pwd: "secure_password_here",
  roles: [
    { role: "readWrite", db: "kerouma_prod" }
  ]
})

// Create indexes for performance
db.users.createIndex({ "phone_number": 1 }, { unique: true })
db.users.createIndex({ "email": 1 }, { unique: true })
db.recipes.createIndex({ "user_id": 1 })
db.recipes.createIndex({ "created_at": -1 })
db.payments.createIndex({ "user_id": 1 })
db.payments.createIndex({ "checkout_id": 1 }, { unique: true })
```

#### 3. Backup Strategy

```bash
# Automated backups (Atlas handles this)
# Point-in-time recovery enabled
# Cross-region backup replication

# Manual backup script
mongodump --uri="mongodb+srv://user:pass@cluster.mongodb.net/kerouma_prod" \
    --out="/backups/$(date +%Y%m%d_%H%M%S)"
```

## Mobile App Deployment

### iOS App Store

#### 1. Prepare for App Store

```bash
# Install EAS CLI
npm install -g @expo/eas-cli

# Configure EAS
eas login
eas build:configure

# Build for iOS
eas build --platform ios --profile production
```

#### 2. App Store Connect Configuration

```json
{
  "expo": {
    "name": "KE-ROUMA",
    "slug": "kerouma",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#2e7d32"
    },
    "updates": {
      "fallbackToCacheTimeout": 0
    },
    "assetBundlePatterns": [
      "**/*"
    ],
    "ios": {
      "supportsTablet": true,
      "bundleIdentifier": "com.kerouma.app",
      "buildNumber": "1"
    },
    "android": {
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png",
        "backgroundColor": "#FFFFFF"
      },
      "package": "com.kerouma.app",
      "versionCode": 1
    }
  }
}
```

### Google Play Store

#### 1. Build for Android

```bash
# Build for Android
eas build --platform android --profile production

# Submit to Play Store
eas submit --platform android
```

#### 2. Play Console Configuration

- Upload APK/AAB to Play Console
- Configure app listing and store presence
- Set up content rating
- Configure pricing and distribution
- Submit for review

## Monitoring and Logging

### 1. Application Monitoring

#### Sentry Integration

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
    environment=os.getenv("ENVIRONMENT", "production")
)
```

#### Health Checks

```python
from fastapi import APIRouter
import psutil
import time

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0",
        "memory_usage": psutil.virtual_memory().percent,
        "cpu_usage": psutil.cpu_percent()
    }

@router.get("/health/detailed")
async def detailed_health():
    # Database connectivity check
    # External API checks
    # Cache status
    pass
```

### 2. Logging Configuration

```python
import logging
import sys
from pythonjsonlogger import jsonlogger

# Configure structured logging
logHandler = logging.StreamHandler(sys.stdout)
formatter = jsonlogger.JsonFormatter(
    "%(asctime)s %(name)s %(levelname)s %(message)s"
)
logHandler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)
```

### 3. Performance Monitoring

```python
from fastapi import Request
import time

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log slow requests
    if process_time > 1.0:
        logger.warning(f"Slow request: {request.url} took {process_time:.2f}s")
    
    return response
```

## SSL/TLS Configuration

### 1. Let's Encrypt (Free SSL)

```bash
# Install Certbot
sudo apt-get update
sudo apt-get install certbot

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 2. CloudFlare SSL (Recommended)

```bash
# Configure CloudFlare DNS
# Enable Full (strict) SSL/TLS encryption
# Enable HSTS
# Configure security headers
```

## Performance Optimization

### 1. Caching Strategy

```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
import redis

# Redis caching
redis_client = redis.Redis(host="redis-host", port=6379, db=0)
FastAPICache.init(RedisBackend(redis_client), prefix="kerouma-cache")

@app.get("/api/recipes/popular")
@cache(expire=3600)  # Cache for 1 hour
async def get_popular_recipes():
    # Expensive database query
    pass
```

### 2. Database Optimization

```python
# Connection pooling
from motor.motor_asyncio import AsyncIOMotorClient

class Database:
    client: AsyncIOMotorClient = None
    
    @classmethod
    async def connect_to_mongo(cls):
        cls.client = AsyncIOMotorClient(
            MONGODB_URL,
            maxPoolSize=10,
            minPoolSize=1,
            maxIdleTimeMS=30000,
            waitQueueTimeoutMS=5000
        )
    
    @classmethod
    async def close_mongo_connection(cls):
        if cls.client:
            cls.client.close()
```

### 3. CDN Configuration

```javascript
// Static asset optimization
const assetConfig = {
  images: {
    domains: ['cdn.yourdomain.com'],
    formats: ['image/webp', 'image/avif'],
    minimumCacheTTL: 86400 // 24 hours
  },
  compress: true,
  poweredByHeader: false
}
```

## Security Hardening

### 1. API Security

```python
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Trusted hosts
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
)

# Rate limiting
@app.get("/api/recipes/generate")
@rate_limiter(times=10, seconds=60)
async def generate_recipe():
    pass
```

### 2. Input Validation

```python
from pydantic import BaseModel, validator
import re

class UserRegistration(BaseModel):
    phone_number: str
    password: str
    full_name: str
    
    @validator('phone_number')
    def validate_phone(cls, v):
        if not re.match(r'^\+254\d{9}$', v):
            raise ValueError('Invalid phone number format')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v
```

## Backup and Disaster Recovery

### 1. Automated Backups

```bash
#!/bin/bash
# backup-script.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/$DATE"

# Database backup
mongodump --uri="$MONGODB_URL" --out="$BACKUP_DIR/database"

# File backup
tar -czf "$BACKUP_DIR/files.tar.gz" /app/uploads

# Upload to cloud storage
aws s3 cp "$BACKUP_DIR" s3://kerouma-backups/ --recursive

# Cleanup old backups (keep last 30 days)
find /backups -type d -mtime +30 -exec rm -rf {} \;
```

### 2. Disaster Recovery Plan

```yaml
# disaster-recovery.yml
recovery_procedures:
  database_failure:
    - Restore from latest MongoDB Atlas backup
    - Update connection strings
    - Verify data integrity
    
  application_failure:
    - Deploy from last known good commit
    - Scale up redundant instances
    - Update load balancer configuration
    
  complete_infrastructure_failure:
    - Activate secondary region deployment
    - Update DNS records
    - Restore from backups
    
recovery_time_objective: 4 hours
recovery_point_objective: 1 hour
```

## Deployment Checklist

### Pre-Deployment

- [ ] Environment variables configured
- [ ] Database migrations completed
- [ ] SSL certificates installed
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] Monitoring and logging setup
- [ ] Backup procedures tested
- [ ] Performance testing completed
- [ ] Security audit passed

### Post-Deployment

- [ ] Health checks passing
- [ ] API endpoints responding
- [ ] Database connectivity verified
- [ ] External integrations working
- [ ] SSL certificate valid
- [ ] Monitoring alerts configured
- [ ] Error tracking functional
- [ ] Performance metrics baseline established
- [ ] User acceptance testing completed

### Rollback Plan

```bash
#!/bin/bash
# rollback-script.sh

# Rollback to previous version
gcloud run services replace previous-service.yaml --region=africa-south1

# Verify rollback
curl -f https://api.yourdomain.com/health

# Update DNS if needed
# Notify team of rollback
```

## Maintenance

### Regular Tasks

- **Weekly**: Review error logs and performance metrics
- **Monthly**: Update dependencies and security patches
- **Quarterly**: Security audit and penetration testing
- **Annually**: Disaster recovery testing

### Scaling Considerations

```python
# Auto-scaling configuration
scaling_config = {
    "min_instances": 2,
    "max_instances": 50,
    "target_cpu_utilization": 70,
    "target_memory_utilization": 80,
    "scale_up_cooldown": "2m",
    "scale_down_cooldown": "5m"
}
```

This deployment guide provides a comprehensive approach to deploying KE-ROUMA in production environments with proper security, monitoring, and maintenance procedures.
