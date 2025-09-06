# Deployment Guide

## 🚀 **MoatMetrics Deployment Documentation**

Complete guide for deploying MoatMetrics in local development, staging, and production environments.

**Document Version**: 1.0.0  
**Last Updated**: September 4, 2025  
**Target Audience**: DevOps Engineers, System Administrators, Developers

---

## 📋 **Prerequisites**

### **System Requirements**

#### **Minimum Requirements**
- **OS**: Windows 10, macOS 10.15, or Linux (Ubuntu 20.04+)
- **Python**: 3.11 or higher
- **Memory**: 4GB RAM
- **Storage**: 10GB available space
- **Network**: Internet connection for initial setup

#### **Recommended Requirements**
- **OS**: Windows 11, macOS 12+, or Linux (Ubuntu 22.04+)
- **Python**: 3.11+ with pip
- **Memory**: 8GB+ RAM
- **Storage**: 50GB+ SSD storage
- **CPU**: Multi-core processor for better performance

### **Dependencies**
- **Git**: Version control for source code
- **Python Virtual Environment**: venv or conda
- **SQLite**: Included with Python (for development)
- **PostgreSQL**: For production deployments
- **Docker**: Optional, for containerized deployment

---

## 🛠️ **Local Development Setup**

### **1. Clone Repository**

```bash
# Clone the MoatMetrics repository
git clone https://github.com/your-org/moatmetrics.git
cd moatmetrics

# Verify directory structure
ls -la
```

### **2. Python Environment Setup**

#### **Windows (PowerShell)**
```powershell
# Create virtual environment
python -m venv moatmetrics_env

# Activate environment
.\moatmetrics_env\Scripts\Activate.ps1

# Verify activation
python --version
pip --version
```

#### **macOS/Linux (Bash/Zsh)**
```bash
# Create virtual environment
python3 -m venv moatmetrics_env

# Activate environment
source moatmetrics_env/bin/activate

# Verify activation
python --version
pip --version
```

### **3. Install Dependencies**

```bash
# Upgrade pip to latest version
pip install --upgrade pip

# Install all project dependencies (includes dev dependencies)
pip install -r requirements.txt

# Verify installation (check a few key packages)
pip list | grep fastapi
pip list | grep pandas
pip list | grep torch
```

### **4. Configuration Setup**

#### **Environment Variables**
Create `.env` file in project root:

```env
# Development Configuration
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# Database Configuration
DATABASE_TYPE=sqlite
DATABASE_URL=sqlite:///./data/moatmetrics_dev.db
DATABASE_ECHO=false

# API Configuration
API_HOST=localhost
API_PORT=8000
API_RELOAD=true

# Analytics Configuration
ANALYTICS_CONFIDENCE_THRESHOLD=0.7
ANALYTICS_ENABLE_SHAP=false
ANALYTICS_MAX_PROCESSING_TIME=30

# Security Configuration
SECRET_KEY=dev-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging Configuration
LOG_ROTATION_SIZE=10 MB
LOG_RETENTION_DAYS=30
```

#### **Database Initialization**
```bash
# Create database directory
mkdir -p data/

# Initialize database (automatic on first run)
python -m src.main

# Verify database creation
ls -la data/
```

### **5. Start Development Server**

```bash
# Start with auto-reload
python -m src.main

# Alternative: Use uvicorn directly
uvicorn src.api.main:app --host localhost --port 8000 --reload

# Verify server is running
curl http://localhost:8000/health
```

**Expected Output:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://localhost:8000 (Press CTRL+C to quit)
```

### **6. Verification Steps**

```bash
# 1. Health check
curl http://localhost:8000/health

# 2. API documentation
# Open browser: http://localhost:8000/docs

# 3. Upload sample data
curl -X POST "http://localhost:8000/api/upload/clients" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_data/clients.csv"

# 4. Run analytics
curl -X POST "http://localhost:8000/api/analytics/run" \
  -H "Content-Type: application/json" \
  -d '{"metric_types": ["profitability"]}'
```

---

## 🐳 **Docker Deployment**

### **1. Using Docker Compose (Recommended)**

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  moatmetrics:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=sqlite:///app/data/moatmetrics.db
      - SECRET_KEY=${SECRET_KEY:-change-me-in-production}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

volumes:
  moatmetrics_data:
    driver: local
```

### **2. Build and Run**

```bash
# Build the Docker image
docker-compose build

# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Health check
curl http://localhost:8000/health

# Stop the application
docker-compose down
```

### **3. Custom Docker Build**

```bash
# Build custom image
docker build -t moatmetrics:latest .

# Run with custom settings
docker run -d \
  --name moatmetrics-app \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e DATABASE_URL=sqlite:///app/data/moatmetrics.db \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  moatmetrics:latest

# Monitor container
docker logs -f moatmetrics-app
```

---

## 🏭 **Production Deployment**

### **1. Server Preparation**

#### **System Updates**
```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv python3-pip nginx certbot

# CentOS/RHEL
sudo dnf update -y
sudo dnf install -y python3.11 python3-pip nginx certbot
```

#### **Create Application User**
```bash
# Create dedicated user for security
sudo useradd --system --home /opt/moatmetrics moatmetrics
sudo mkdir -p /opt/moatmetrics
sudo chown moatmetrics:moatmetrics /opt/moatmetrics
```

### **2. Application Deployment**

```bash
# Switch to application user
sudo su - moatmetrics

# Clone repository
git clone https://github.com/your-org/moatmetrics.git /opt/moatmetrics/app
cd /opt/moatmetrics/app

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --no-cache-dir -r requirements.txt

# Create production directories
mkdir -p /opt/moatmetrics/{data,logs,backups}
```

### **3. Production Configuration**

#### **Environment Variables**
Create `/opt/moatmetrics/.env`:

```env
# Production Configuration
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Database Configuration (PostgreSQL)
DATABASE_TYPE=postgresql
DATABASE_URL=postgresql://moatmetrics_user:secure_password@localhost:5432/moatmetrics_prod
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false

# Security Configuration
SECRET_KEY=your-very-secure-secret-key-256-bit
ACCESS_TOKEN_EXPIRE_MINUTES=60
ALLOWED_HOSTS=["your-domain.com", "api.your-domain.com"]

# Analytics Configuration
ANALYTICS_CONFIDENCE_THRESHOLD=0.8
ANALYTICS_ENABLE_SHAP=false
ANALYTICS_MAX_PROCESSING_TIME=60

# Logging Configuration
LOG_ROTATION_SIZE=100 MB
LOG_RETENTION_DAYS=90
LOG_COMPRESS=true

# Monitoring Configuration
METRICS_ENABLED=true
PROMETHEUS_PORT=9090
```

#### **PostgreSQL Setup**
```bash
# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql -c "CREATE DATABASE moatmetrics_prod;"
sudo -u postgres psql -c "CREATE USER moatmetrics_user WITH PASSWORD 'secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE moatmetrics_prod TO moatmetrics_user;"

# Test connection
psql -h localhost -U moatmetrics_user -d moatmetrics_prod -c "\dt"
```

### **4. Process Management with Systemd**

Create `/etc/systemd/system/moatmetrics.service`:

```ini
[Unit]
Description=MoatMetrics Analytics Platform
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=simple
User=moatmetrics
Group=moatmetrics
WorkingDirectory=/opt/moatmetrics/app
Environment=PATH=/opt/moatmetrics/app/venv/bin
EnvironmentFile=/opt/moatmetrics/.env
ExecStart=/opt/moatmetrics/app/venv/bin/python -m src.main
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal
SyslogIdentifier=moatmetrics

[Install]
WantedBy=multi-user.target
```

#### **Service Management**
```bash
# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable moatmetrics.service

# Start the service
sudo systemctl start moatmetrics

# Check status
sudo systemctl status moatmetrics

# View logs
sudo journalctl -u moatmetrics -f

# Restart service
sudo systemctl restart moatmetrics
```

### **5. Reverse Proxy with Nginx**

Create `/etc/nginx/sites-available/moatmetrics`:

```nginx
server {
    listen 80;
    server_name your-domain.com api.your-domain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com api.your-domain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Security Headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    
    # File Upload Configuration
    client_max_body_size 100M;
    client_body_timeout 60s;
    client_header_timeout 60s;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Static files (if applicable)
    location /static/ {
        alias /opt/moatmetrics/app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Health check endpoint (no auth required)
    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }
}
```

#### **Enable Site and SSL**
```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/moatmetrics /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com -d api.your-domain.com

# Test SSL renewal
sudo certbot renew --dry-run
```

---

## 🔧 **Environment-Specific Configurations**

### **Development Environment**

```env
# .env.development
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
DATABASE_URL=sqlite:///./data/moatmetrics_dev.db
API_RELOAD=true
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
```

**Start Command:**
```bash
python -m src.main --env development --reload
```

### **Staging Environment**

```env
# .env.staging
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO
DATABASE_URL=postgresql://moatmetrics_user:password@staging-db:5432/moatmetrics_staging
API_RELOAD=false
CORS_ORIGINS=["https://staging.your-domain.com"]
```

**Start Command:**
```bash
python -m src.main --env staging
```

### **Production Environment**

```env
# .env.production
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
DATABASE_URL=postgresql://moatmetrics_user:secure_password@prod-db:5432/moatmetrics_prod
API_RELOAD=false
CORS_ORIGINS=["https://your-domain.com"]
TRUSTED_HOSTS=["your-domain.com", "api.your-domain.com"]
```

**Start Command:**
```bash
python -m src.main --env production
```

---

## 🐳 **Container Deployment**

### **1. Dockerfile**

The project includes a production-ready Dockerfile:

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY sample_data/ ./sample_data/

# Create directories
RUN mkdir -p /app/data /app/logs

# Set environment variables
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["python", "-m", "src.main"]
```

### **2. Docker Compose for Production**

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://moatmetrics:${DB_PASSWORD}@db:5432/moatmetrics
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - app_data:/app/data
      - app_logs:/app/logs
    depends_on:
      - db
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=moatmetrics
      - POSTGRES_USER=moatmetrics
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - db_data:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U moatmetrics"]
      interval: 10s
      timeout: 5s
      retries: 5

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/ssl/certs:ro
      - nginx_logs:/var/log/nginx
    depends_on:
      - app
    restart: unless-stopped

volumes:
  app_data:
  app_logs:
  db_data:
  nginx_logs:
```

### **3. Environment Configuration**

Create `.env.docker`:

```env
# Docker Environment Variables
DB_PASSWORD=very-secure-database-password
SECRET_KEY=your-production-secret-key-256-bit
```

**Deployment Commands:**
```bash
# Production deployment
docker-compose --env-file .env.docker up -d

# View logs
docker-compose logs -f app

# Scale application
docker-compose up -d --scale app=3

# Update application
docker-compose pull
docker-compose up -d
```

---

## ☁️ **Cloud Deployment**

### **AWS Deployment**

#### **1. EC2 Instance Setup**
```bash
# Launch Ubuntu 22.04 LTS instance (t3.medium recommended)
# Configure security groups: HTTP (80), HTTPS (443), SSH (22)

# Connect and setup
ssh -i your-key.pem ubuntu@your-ec2-instance

# Install Docker and Docker Compose
sudo apt update
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### **2. Application Deployment**
```bash
# Clone and deploy
git clone https://github.com/your-org/moatmetrics.git
cd moatmetrics

# Set environment variables
export DB_PASSWORD=$(openssl rand -base64 32)
export SECRET_KEY=$(openssl rand -base64 32)

# Deploy
docker-compose --env-file .env.docker up -d

# Configure domain and SSL
sudo snap install certbot --classic
sudo certbot --nginx -d your-domain.com
```

### **Azure Deployment**

#### **Container Instances**
```bash
# Create resource group
az group create --name moatmetrics-rg --location eastus

# Deploy container
az container create \
  --resource-group moatmetrics-rg \
  --name moatmetrics-app \
  --image your-registry/moatmetrics:latest \
  --cpu 2 \
  --memory 4 \
  --ports 8000 \
  --environment-variables \
    ENVIRONMENT=production \
    DATABASE_URL="your-database-connection-string" \
  --restart-policy Always
```

### **Google Cloud Platform**

#### **Cloud Run Deployment**
```bash
# Build and push to Container Registry
docker build -t gcr.io/your-project/moatmetrics .
docker push gcr.io/your-project/moatmetrics

# Deploy to Cloud Run
gcloud run deploy moatmetrics \
  --image gcr.io/your-project/moatmetrics \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 10 \
  --set-env-vars ENVIRONMENT=production
```

---

## 📊 **Monitoring & Logging**

### **Application Monitoring**

#### **Health Monitoring Script**
```bash
#!/bin/bash
# health_monitor.sh

HEALTH_URL="http://localhost:8000/health"
LOG_FILE="/var/log/moatmetrics/health_monitor.log"

while true; do
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_URL")
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    
    if [ "$RESPONSE" = "200" ]; then
        echo "$TIMESTAMP - OK: Health check passed" >> "$LOG_FILE"
    else
        echo "$TIMESTAMP - ERROR: Health check failed (HTTP $RESPONSE)" >> "$LOG_FILE"
        # Send alert (configure your alerting system)
        # curl -X POST your-webhook-url -d "MoatMetrics health check failed"
    fi
    
    sleep 30
done
```

#### **Log Monitoring with rsyslog**
```bash
# Create rsyslog configuration
sudo tee /etc/rsyslog.d/50-moatmetrics.conf > /dev/null <<EOF
if \$programname startswith 'moatmetrics' then /var/log/moatmetrics/app.log
& stop
EOF

sudo systemctl restart rsyslog
```

### **Performance Monitoring**

#### **Resource Usage Script**
```bash
#!/bin/bash
# monitor_resources.sh

while true; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    
    # CPU and Memory usage
    STATS=$(ps aux | grep 'python.*moatmetrics' | grep -v grep | awk '{cpu+=$3; mem+=$4} END {printf "%.1f %.1f", cpu, mem}')
    
    # Log to file
    echo "$TIMESTAMP - CPU: ${STATS%% *}%, Memory: ${STATS##* }%" >> /var/log/moatmetrics/performance.log
    
    sleep 60
done
```

---

## 🔒 **Security Configuration**

### **SSL/TLS Setup**

#### **Let's Encrypt (Free SSL)**
```bash
# Install Certbot
sudo snap install certbot --classic

# Obtain certificate
sudo certbot --nginx -d your-domain.com -d api.your-domain.com

# Auto-renewal setup
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

#### **Custom SSL Certificate**
```bash
# Place certificates in /etc/ssl/certs/
sudo cp your-domain.crt /etc/ssl/certs/
sudo cp your-domain.key /etc/ssl/private/
sudo chmod 644 /etc/ssl/certs/your-domain.crt
sudo chmod 600 /etc/ssl/private/your-domain.key
```

### **Firewall Configuration**

```bash
# UFW (Ubuntu)
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw status

# iptables (Alternative)
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables -A INPUT -j DROP
```

### **Database Security**

```bash
# PostgreSQL security
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'secure-postgres-admin-password';"

# Configure pg_hba.conf for restricted access
sudo nano /etc/postgresql/15/main/pg_hba.conf
# Change: local all all trust
# To: local all all md5
```

---

## 💾 **Backup & Recovery**

### **Database Backup**

#### **Automated Backup Script**
```bash
#!/bin/bash
# backup_database.sh

BACKUP_DIR="/opt/moatmetrics/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATABASE_URL="postgresql://moatmetrics_user:password@localhost:5432/moatmetrics_prod"

# Create backup
pg_dump "$DATABASE_URL" | gzip > "$BACKUP_DIR/moatmetrics_backup_$TIMESTAMP.sql.gz"

# Cleanup old backups (keep 30 days)
find "$BACKUP_DIR" -name "moatmetrics_backup_*.sql.gz" -mtime +30 -delete

# Log backup
echo "$(date '+%Y-%m-%d %H:%M:%S') - Database backup completed: moatmetrics_backup_$TIMESTAMP.sql.gz" >> /var/log/moatmetrics/backup.log
```

#### **Cron Schedule**
```bash
# Daily backups at 2 AM
sudo crontab -e
# Add: 0 2 * * * /opt/moatmetrics/scripts/backup_database.sh
```

### **Application Data Backup**

```bash
#!/bin/bash
# backup_data.sh

BACKUP_DIR="/opt/moatmetrics/backups"
APP_DATA_DIR="/opt/moatmetrics/data"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Backup application data
tar -czf "$BACKUP_DIR/app_data_$TIMESTAMP.tar.gz" -C "$APP_DATA_DIR" .

# Backup logs
tar -czf "$BACKUP_DIR/logs_$TIMESTAMP.tar.gz" -C "/opt/moatmetrics/logs" .

# Cleanup old data backups (keep 7 days)
find "$BACKUP_DIR" -name "app_data_*.tar.gz" -mtime +7 -delete
find "$BACKUP_DIR" -name "logs_*.tar.gz" -mtime +7 -delete
```

### **Recovery Procedures**

#### **Database Recovery**
```bash
# Stop application
sudo systemctl stop moatmetrics

# Restore database
gunzip -c /opt/moatmetrics/backups/moatmetrics_backup_20250904_020000.sql.gz | \
  psql postgresql://moatmetrics_user:password@localhost:5432/moatmetrics_prod

# Restart application
sudo systemctl start moatmetrics
```

#### **Application Data Recovery**
```bash
# Stop application
sudo systemctl stop moatmetrics

# Restore data
cd /opt/moatmetrics
tar -xzf backups/app_data_20250904_020000.tar.gz -C data/

# Restart application
sudo systemctl start moatmetrics
```

---

## 🔍 **Verification & Testing**

### **Post-Deployment Verification**

#### **1. System Health Checks**
```bash
# Application health
curl -f http://localhost:8000/health

# Database connectivity
python3 -c "
import psycopg2
conn = psycopg2.connect('postgresql://moatmetrics_user:password@localhost:5432/moatmetrics_prod')
print('Database connection: OK')
conn.close()
"

# Service status
sudo systemctl status moatmetrics
sudo systemctl status nginx
sudo systemctl status postgresql
```

#### **2. Functional Testing**
```bash
# Upload test data
curl -X POST "http://localhost:8000/api/upload/clients" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_data/clients.csv"

# Run analytics
curl -X POST "http://localhost:8000/api/analytics/run" \
  -H "Content-Type: application/json" \
  -d '{"metric_types": ["profitability"]}'

# Verify results
curl http://localhost:8000/api/analytics/results | jq .
```

#### **3. Performance Testing**
```bash
# Install Apache Bench
sudo apt install apache2-utils

# Load testing
ab -n 1000 -c 10 http://localhost:8000/health

# Concurrent upload testing
for i in {1..5}; do
  curl -X POST "http://localhost:8000/api/upload/clients" \
    -H "Content-Type: multipart/form-data" \
    -F "file=@sample_data/clients.csv" &
done
wait
```

---

## 🚨 **Troubleshooting**

### **Common Deployment Issues**

#### **Port Already in Use**
```bash
# Find process using port 8000
sudo lsof -i :8000
# or
sudo netstat -tulpn | grep :8000

# Kill process
sudo kill -9 <process_id>

# Restart MoatMetrics
sudo systemctl restart moatmetrics
```

#### **Database Connection Failed**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection manually
psql -h localhost -U moatmetrics_user -d moatmetrics_prod

# Check logs
sudo journalctl -u postgresql -f
tail -f /var/log/moatmetrics/app.log
```

#### **Permission Denied Errors**
```bash
# Fix file permissions
sudo chown -R moatmetrics:moatmetrics /opt/moatmetrics/
sudo chmod -R 755 /opt/moatmetrics/app/
sudo chmod 600 /opt/moatmetrics/.env

# Fix log directory permissions
sudo mkdir -p /var/log/moatmetrics
sudo chown moatmetrics:moatmetrics /var/log/moatmetrics
```

#### **SSL Certificate Issues**
```bash
# Check certificate status
sudo certbot certificates

# Test SSL configuration
sudo nginx -t
curl -I https://your-domain.com

# Renew certificates
sudo certbot renew --force-renewal
sudo systemctl reload nginx
```

### **Performance Issues**

#### **High CPU Usage**
```bash
# Monitor processes
htop
ps aux | grep moatmetrics | head -10

# Check analytics queue
curl http://localhost:8000/api/analytics/status
```

#### **High Memory Usage**
```bash
# Monitor memory
free -h
ps aux --sort=-%mem | head

# Check for memory leaks in logs
grep -i "memory\|leak" /var/log/moatmetrics/app.log
```

#### **Database Performance**
```bash
# PostgreSQL performance monitoring
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"

# Check slow queries
sudo -u postgres psql -c "SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
```

---

## 📋 **Environment Variables Reference**

### **Core Configuration**

| **Variable** | **Required** | **Default** | **Description** |
|---|---|---|---|
| `ENVIRONMENT` | Yes | `development` | Deployment environment |
| `DEBUG` | No | `false` | Enable debug mode |
| `LOG_LEVEL` | No | `INFO` | Logging level |
| `SECRET_KEY` | Yes | None | Application secret key |

### **Database Configuration**

| **Variable** | **Required** | **Default** | **Description** |
|---|---|---|---|
| `DATABASE_TYPE` | Yes | `sqlite` | Database type |
| `DATABASE_URL` | Yes | None | Database connection string |
| `DATABASE_POOL_SIZE` | No | `10` | Connection pool size |
| `DATABASE_ECHO` | No | `false` | Log database queries |

### **API Configuration**

| **Variable** | **Required** | **Default** | **Description** |
|---|---|---|---|
| `API_HOST` | No | `localhost` | API bind host |
| `API_PORT` | No | `8000` | API port |
| `API_RELOAD` | No | `false` | Auto-reload on changes |
| `CORS_ORIGINS` | No | `[]` | Allowed CORS origins |

### **Analytics Configuration**

| **Variable** | **Required** | **Default** | **Description** |
|---|---|---|---|
| `ANALYTICS_CONFIDENCE_THRESHOLD` | No | `0.7` | Review threshold |
| `ANALYTICS_ENABLE_SHAP` | No | `false` | Enable SHAP (future) |
| `ANALYTICS_MAX_PROCESSING_TIME` | No | `30` | Max processing time (seconds) |

---

## 🔄 **Maintenance & Updates**

### **Application Updates**

#### **Rolling Update (Zero Downtime)**
```bash
# 1. Pull latest code
git pull origin main

# 2. Build new image
docker build -t moatmetrics:latest .

# 3. Update with zero downtime
docker-compose up -d --no-deps app

# 4. Verify deployment
curl http://localhost:8000/health
docker-compose logs -f app
```

#### **Database Migrations**
```bash
# Backup before migration
./scripts/backup_database.sh

# Run migration (when available)
python -m alembic upgrade head

# Verify migration
python -c "from src.db.models import *; print('Migration successful')"
```

### **Security Updates**

```bash
# System updates
sudo apt update && sudo apt upgrade -y

# Python dependencies
pip install --upgrade -r requirements.txt

# Docker base image updates
docker pull python:3.11-slim
docker-compose build --no-cache
```

---

## 📞 **Support & Resources**

### **Deployment Support**
- **GitHub Issues**: Report deployment problems
- **Documentation**: Complete troubleshooting guide
- **Community**: Discord channel for deployment questions

### **Production Support**
- **Email**: devops@moatmetrics.com
- **Emergency**: +1-800-MOAT-OPS
- **Status Page**: https://status.moatmetrics.com

### **Additional Resources**
- **Infrastructure Templates**: Terraform and CloudFormation examples
- **Monitoring Dashboards**: Grafana dashboard configurations
- **Security Guidelines**: Complete security hardening guide

---

**This deployment guide covers all aspects of MoatMetrics deployment from local development to enterprise production environments. Follow the appropriate section for your deployment scenario.** 🚀

---

**Document Status**: Production Ready  
**Next Review**: October 1, 2025  
**Maintainer**: DevOps Team
