# Quick Start Guide

## 🚀 **Get MoatMetrics Running in 5 Minutes**

This guide will get you up and running with MoatMetrics on your local machine in under 5 minutes.

---

## 📋 **Prerequisites**

Before starting, ensure you have:

- **Python 3.11 or higher** ([Download here](https://www.python.org/downloads/))
- **Git** ([Download here](https://git-scm.com/downloads))
- **2GB RAM minimum** (4GB recommended)
- **1GB available disk space**

### **Verify Prerequisites**

```bash
# Check Python version (should be 3.11+)
python --version

# Check Git installation
git --version
```

---

## ⚡ **Quick Installation**

### **Step 1: Clone the Repository**

```bash
# Clone MoatMetrics repository
git clone https://github.com/yourusername/moatmetrics.git
cd moatmetrics
```

### **Step 2: Create Virtual Environment**

```bash
# Create virtual environment
python -m venv moatmetrics_env

# Activate virtual environment
# Windows:
moatmetrics_env\Scripts\activate

# macOS/Linux:
source moatmetrics_env/bin/activate
```

You should see `(moatmetrics_env)` in your terminal prompt.

### **Step 3: Install Dependencies**

```bash
# Install all required packages
pip install -r requirements.txt
```

### **Step 4: Start MoatMetrics**

```bash
# Launch the application
python main.py
```

You should see output similar to:

```
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║     ███╗   ███╗ ██████╗  █████╗ ████████╗                     ║
║     ████╗ ████║██╔═══██╗██╔══██╗╚══██╔══╝                     ║
║     ██╔████╔██║██║   ██║███████║   ██║                        ║
║     ██║╚██╔╝██║██║   ██║██╔══██║   ██║                        ║
║     ██║ ╚═╝ ██║╚██████╔╝██║  ██║   ██║                        ║
║                                                                  ║
║     ███╗   ███╗███████╗████████╗██████╗ ██████╗ ██████╗███████╗ ║
║     ████╗ ████║██╔════╝╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██╔════╝ ║
║     ██╔████╔██║█████╗     ██║   ██████╔╝██████╔╝██║     ███████╗ ║
║     ██║╚██╔╝██║██╔══╝     ██║   ██╔══██╗██╔══██╗██║     ╚════██║ ║
║     ██║ ╚═╝ ██║███████╗   ██║   ██║  ██║██║  ██║╚██████╗███████║ ║
║                                                                  ║
║          Privacy-First Offline Analytics Platform               ║
║                    for MSPs - MVP v1.0.0                       ║
╚══════════════════════════════════════════════════════════════════╝

📡 API Documentation: http://localhost:8000/docs
📊 Interactive API: http://localhost:8000/redoc
❤️  Health Check: http://localhost:8000/health
```

---

## ✅ **Verify Installation**

### **Test 1: Health Check**

```bash
# Check if MoatMetrics is running (in a new terminal)
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","timestamp":"2025-09-04T15:55:30Z","version":"1.0.0-prototype"}
```

### **Test 2: Open Web Interface**

Open your browser and navigate to:
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

You should see the interactive FastAPI documentation.

---

## 📊 **Load Sample Data**

### **Step 1: Prepare Sample Data**

MoatMetrics includes sample CSV files for testing:

```bash
# List available sample data
ls moatmetrics/data/raw/

# You should see:
# clients.csv
# invoices.csv
# time_logs.csv
# licenses.csv
```

### **Step 2: Upload Data via API**

#### **Option A: Using the Web Interface**

1. Go to http://localhost:8000/docs
2. Find the `/api/upload/{data_type}` endpoint
3. Click "Try it out"
4. Select data type (e.g., "clients")
5. Upload the corresponding CSV file
6. Click "Execute"

#### **Option B: Using PowerShell Script**

```bash
# Run the provided upload script
powershell -ExecutionPolicy Bypass -File upload_data.ps1
```

#### **Option C: Using cURL**

```bash
# Upload clients data
curl -X POST "http://localhost:8000/api/upload/clients?validate_schema=false" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@moatmetrics/data/raw/clients.csv"

# Upload invoices data
curl -X POST "http://localhost:8000/api/upload/invoices?validate_schema=false" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@moatmetrics/data/raw/invoices.csv"

# Upload time logs data
curl -X POST "http://localhost:8000/api/upload/time_logs?validate_schema=false" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@moatmetrics/data/raw/time_logs.csv"

# Upload licenses data
curl -X POST "http://localhost:8000/api/upload/licenses?validate_schema=false" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@moatmetrics/data/raw/licenses.csv"
```

### **Step 3: Verify Data Upload**

```bash
# Run database verification script (now in scripts directory)
python scripts/verify_db.py

# Expected output:
# 📊 Database Verification
# ========================
#    👥 clients: 10 records
#    📄 invoices: 50 records
#    ⏰ time_logs: 200 records
#    🔑 licenses: 30 records
```

---

## 🧮 **Run Analytics**

### **Step 1: Trigger Analytics Run**

```bash
# Run analytics test script
python test_analytics.py

# Expected output:
# 🔬 Testing Analytics Run
# =========================
# ✅ Analytics run completed successfully!
# 📊 Snapshot ID: [unique-id]
# 📈 Metrics computed: 3
```

### **Step 2: View Results via API**

Go to http://localhost:8000/docs and try the `/api/analytics/results` endpoint to see the computed metrics.

---

## 📁 **Project Structure**

After installation, your project structure will look like:

```
moatmetrics/
├── 📁 config/              # Configuration files
├── 📁 src/                 # Source code
│   ├── api/               # FastAPI endpoints
│   ├── analytics/         # Analytics engine
│   ├── etl/              # Data processing
│   ├── governance/       # Policy engine
│   └── utils/            # Shared utilities
├── 📁 data/               # Data storage
│   ├── moatmetrics.db    # SQLite database
│   └── snapshots/        # Data versioning
├── 📁 docs/               # Documentation
├── 📁 logs/               # Application logs
├── 📁 reports/            # Generated reports
└── main.py               # Application entry point
```

---

## 🔧 **Configuration**

### **Default Configuration**

MoatMetrics works out-of-the-box with sensible defaults. The main configuration file is `config/config.yaml`:

```yaml
app:
  name: "MoatMetrics"
  version: "1.0.0-prototype"
  environment: "development"
  debug: true

api:
  host: "localhost"
  port: 8000

database:
  url: "sqlite:///data/moatmetrics.db"

analytics:
  confidence_threshold: 0.7
```

### **Environment Variables**

You can override configuration with environment variables:

```bash
# Example: Change API port
export MOATMETRICS_API_PORT=8080

# Example: Set production mode
export MOATMETRICS_APP_DEBUG=false
```

---

## 🌐 **Available Endpoints**

Once running, MoatMetrics provides these key endpoints:

| **Endpoint** | **Purpose** | **Example** |
|---|---|---|
| `/health` | System health check | `GET /health` |
| `/api/upload/{type}` | Upload CSV data | `POST /api/upload/clients` |
| `/api/analytics/run` | Run analytics | `POST /api/analytics/run` |
| `/api/analytics/results` | Get results | `GET /api/analytics/results` |
| `/api/clients` | Manage clients | `GET /api/clients` |
| `/docs` | API documentation | Browser: http://localhost:8000/docs |

---

## 🛠️ **Development Mode**

### **Enable Debug Logging**

```bash
# Set environment variable for verbose logging
export MOATMETRICS_APP_DEBUG=true
```

### **Auto-Reload on Changes**

```bash
# Start with auto-reload (development only)
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### **Database Reset**

```bash
# Reset database (WARNING: This deletes all data)
rm data/moatmetrics.db
python -c "from src.utils.database import get_db_manager; get_db_manager()"
```

---

## 📱 **Next Steps**

### **1. Explore the API**
- Visit http://localhost:8000/docs
- Try different endpoints
- Upload your own data

### **2. Run Analytics**
- Use the analytics endpoints
- Explore confidence scoring
- Review explanations

### **3. Generate Reports**
- Use the reporting endpoints
- Download generated reports
- Customize report parameters

### **4. Read Documentation**
- [Architecture Guide](ARCHITECTURE.md)
- [API Reference](API.md)
- [User Guide](USER_GUIDE.md)

---

## 🆘 **Need Help?**

### **Common Issues**
- See [Troubleshooting Guide](TROUBLESHOOTING.md)
- Check [Challenges & Fixes](CHALLENGES_AND_FIXES.md)

### **Support**
- 📧 **Email**: support@moatmetrics.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/moatmetrics/issues)
- 📖 **Documentation**: Complete docs in `/docs` folder

---

## ✨ **What's Next?**

After completing this quick start:

1. **✅ MoatMetrics is running locally**
2. **✅ Sample data is loaded**
3. **✅ Analytics are working**
4. **✅ You can explore the API**

You're now ready to:
- Upload your own MSP data
- Run customized analytics
- Generate business reports
- Integrate with your existing systems

**Congratulations! You're now running MoatMetrics! 🎉**
