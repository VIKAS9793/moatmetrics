# Troubleshooting Guide

## 🔧 **Common Issues and Solutions**

This guide covers the most frequently encountered issues when setting up and running MoatMetrics, along with step-by-step solutions.

---

## 🚀 **Installation Issues**

### **Issue 1: Python Version Compatibility**

#### **Problem:**
```bash
ERROR: This package requires Python >=3.11
```

#### **Solution:**
```bash
# Check your Python version
python --version

# If version is < 3.11, upgrade Python
# Windows: Download from https://www.python.org/downloads/
# macOS: brew install python@3.11
# Ubuntu: sudo apt-get install python3.11

# Use specific Python version
python3.11 -m venv moatmetrics_env
```

### **Issue 2: Virtual Environment Activation Problems**

#### **Problem (Windows):**
```bash
cannot be loaded because running scripts is disabled on this system
```

#### **Solution:**
```bash
# Enable script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate
moatmetrics_env\Scripts\activate
```

#### **Problem (macOS/Linux):**
```bash
source: command not found
```

#### **Solution:**
```bash
# Use dot instead of source
. moatmetrics_env/bin/activate

# Or use full path
/bin/bash moatmetrics_env/bin/activate
```

### **Issue 3: Dependency Installation Failures**

#### **Problem:**
```bash
ERROR: Failed building wheel for [package]
```

#### **Solution:**
```bash
# Upgrade pip and setuptools first
pip install --upgrade pip setuptools wheel

# Install with verbose output to see errors
pip install -r requirements.txt -v

# If specific package fails, install individually
pip install pandas numpy scikit-learn
```

---

## 🗄️ **Database Issues**

### **Issue 4: Database Permission Errors**

#### **Problem:**
```bash
PermissionError: [Errno 13] Permission denied: 'data/moatmetrics.db'
```

#### **Solution:**
```bash
# Check file permissions
ls -la data/

# Fix permissions (Unix/Linux/macOS)
chmod 664 data/moatmetrics.db
chmod 755 data/

# Windows: Right-click → Properties → Security → Give full control
```

### **Issue 5: Database Lock Errors**

#### **Problem:**
```bash
sqlite3.OperationalError: database is locked
```

#### **Solution:**
```bash
# Stop all MoatMetrics processes
# Windows:
taskkill /F /IM python.exe

# macOS/Linux:
pkill -f moatmetrics

# Remove lock file if exists
rm data/moatmetrics.db-wal
rm data/moatmetrics.db-shm

# Restart application
python main.py
```

### **Issue 6: Database Corruption**

#### **Problem:**
```bash
sqlite3.DatabaseError: database disk image is malformed
```

#### **Solution:**
```bash
# Backup current database
cp data/moatmetrics.db data/moatmetrics.db.backup

# Check database integrity
sqlite3 data/moatmetrics.db "PRAGMA integrity_check;"

# If corrupted, restore from backup or recreate
rm data/moatmetrics.db
python -c "from src.utils.database import get_db_manager; get_db_manager()"
```

---

## 🌐 **API and Network Issues**

### **Issue 7: Port Already in Use**

#### **Problem:**
```bash
OSError: [Errno 48] Address already in use
```

#### **Solution:**
```bash
# Find process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:8000 | xargs kill -9

# Or use different port
export MOATMETRICS_API_PORT=8001
python main.py
```

### **Issue 8: API Not Accessible**

#### **Problem:**
Cannot access http://localhost:8000/health

#### **Solution:**
```bash
# Check if service is running
ps aux | grep python

# Check firewall settings
# Windows: Allow Python through Windows Defender
# macOS: System Preferences → Security & Privacy → Firewall
# Linux: sudo ufw allow 8000

# Check host binding
# Edit config/config.yaml:
api:
  host: "0.0.0.0"  # Instead of "localhost"
  port: 8000
```

### **Issue 9: CORS Issues**

#### **Problem:**
```bash
Access to fetch blocked by CORS policy
```

#### **Solution:**
```bash
# Add your domain to CORS origins in config/config.yaml:
api:
  cors_origins:
    - "http://localhost:3000"
    - "https://yourdomain.com"

# Or allow all origins (development only):
api:
  cors_origins: ["*"]
```

---

## 📊 **Data Processing Issues**

### **Issue 10: CSV Upload Failures**

#### **Problem:**
```bash
UnicodeDecodeError: 'utf-8' codec can't decode byte
```

#### **Solution:**
```bash
# Check file encoding
file -I your_file.csv

# Convert to UTF-8
# Windows: Use Notepad++ → Encoding → Convert to UTF-8
# macOS/Linux:
iconv -f ISO-8859-1 -t UTF-8 input.csv > output.csv

# Or specify encoding in upload:
# Use validate_schema=false and let MoatMetrics auto-detect
```

### **Issue 11: Data Validation Errors**

#### **Problem:**
```json
{"error": "Invalid date format in row 15"}
```

#### **Solution:**
```bash
# Check data format requirements:
# Dates: YYYY-MM-DD or MM/DD/YYYY
# Numbers: No currency symbols or commas
# Client names: Must exist in clients table first

# Upload in correct order:
1. clients.csv
2. invoices.csv  
3. time_logs.csv
4. licenses.csv

# Use validate_schema=false for lenient processing
```

### **Issue 12: Empty Database After Upload**

#### **Problem:**
Upload shows success but database has no records

#### **Solution:**
```bash
# This was a known bug (now fixed) - ensure you have latest code
git pull origin main

# Verify session management in get_db_session():
# Should commit transactions before closing

# Re-upload data with fixed code
```

---

## 🧮 **Analytics Issues**

### **Issue 13: Analytics Run Failures**

#### **Problem:**
```bash
KeyError: 'client_id'
```

#### **Solution:**
```bash
# Ensure data exists in correct date range
python verify_db.py

# Check your date range in analytics request:
{
  "client_ids": [1, 2, 3],
  "start_date": "2025-01-01T00:00:00",  # Use correct year
  "end_date": "2025-12-31T23:59:59"
}

# This specific bug has been fixed in latest version
```

### **Issue 14: Low Confidence Scores**

#### **Problem:**
All analytics results showing low confidence

#### **Solution:**
```bash
# This is expected behavior with limited sample data
# Confidence improves with:
1. More historical data points
2. Better data quality
3. Complete client information

# Adjust confidence threshold:
{
  "confidence_threshold": 0.5  # Lower threshold
}
```

### **Issue 15: JSON Serialization Errors**

#### **Problem:**
```bash
TypeError: numpy.bool_ object is not iterable
```

#### **Solution:**
```bash
# This bug has been fixed in latest version
# Ensure you have the updated analytics engine with convert_numpy_types()

# If still occurring, restart the API server:
# Stop current process and run:
python main.py
```

---

## 🔧 **Performance Issues**

### **Issue 16: Slow Upload Processing**

#### **Problem:**
Large CSV files taking too long to process

#### **Solution:**
```bash
# Increase chunk size for large files
# Edit src/etl/csv_processor.py:
CHUNK_SIZE = 50000  # Increase from default

# Use more memory:
export MOATMETRICS_MEMORY_LIMIT=4GB

# Process files in smaller batches
split -l 10000 large_file.csv smaller_file_
```

### **Issue 17: High Memory Usage**

#### **Problem:**
Python process consuming excessive memory

#### **Solution:**
```bash
# Monitor memory usage:
# Windows: Task Manager
# macOS: Activity Monitor  
# Linux: htop or ps aux

# Optimize memory settings:
export PANDAS_MEMORY_LIMIT=2GB

# Restart service periodically for large processing:
# Implement auto-restart for production
```

### **Issue 18: Slow API Responses**

#### **Problem:**
API endpoints taking >30 seconds to respond

#### **Solution:**
```bash
# Enable query optimization in config/config.yaml:
database:
  pool_size: 10
  max_overflow: 20
  pool_pre_ping: true

# Add database indexes:
python -c "
from src.utils.database import get_db_manager
db = get_db_manager()
# Indexes are already added in latest version
"

# Use async endpoints for long-running operations
```

---

## 📝 **Logging and Debugging**

### **Issue 19: Missing Log Files**

#### **Problem:**
No logs being generated in logs/ directory

#### **Solution:**
```bash
# Check logs directory exists:
mkdir -p logs

# Verify logging configuration:
# logs/ directory should contain:
# - app.log (general application logs)
# - errors.log (error-specific logs)

# Enable debug logging:
export MOATMETRICS_LOG_LEVEL=DEBUG
python main.py
```

### **Issue 20: Cannot Find Error Cause**

#### **Problem:**
Application failing with no clear error message

#### **Solution:**
```bash
# Enable verbose logging:
export MOATMETRICS_APP_DEBUG=true
python main.py

# Check all log files:
tail -f logs/app.log
tail -f logs/errors.log

# Run with Python debugging:
python -u main.py  # Unbuffered output
```

---

## 🔍 **Development Issues**

### **Issue 21: Auto-reload Not Working**

#### **Problem:**
Changes to code not reflected without manual restart

#### **Solution:**
```bash
# Use development server:
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Or set debug mode:
export MOATMETRICS_APP_DEBUG=true
python main.py
```

### **Issue 22: Import Errors**

#### **Problem:**
```bash
ModuleNotFoundError: No module named 'src.utils'
```

#### **Solution:**
```bash
# Ensure you're in the project root directory:
pwd  # Should show /path/to/moatmetrics

# Check Python path:
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or run from project root:
cd /path/to/moatmetrics
python main.py
```

---

## 🔐 **Security and Access Issues**

### **Issue 23: Permission Denied Errors**

#### **Problem:**
```bash
403 Forbidden: Permission denied
```

#### **Solution:**
```bash
# Check role-based access control
# Default user has 'admin' role with full access

# Verify in src/api/main.py:
def get_current_user():
    return {"username": "admin", "role": "admin"}

# For production, implement proper authentication
```

### **Issue 24: File Upload Security Errors**

#### **Problem:**
File uploads being rejected for security reasons

#### **Solution:**
```bash
# Check file extension whitelist:
# Allowed: .csv, .xlsx
# Denied: .exe, .js, .php, etc.

# Check file size limits:
# Default: 100MB max
# Configure in config/config.yaml:
api:
  max_upload_size: 104857600  # 100MB in bytes
```

---

## 📞 **Getting Help**

### **When to Seek Support:**
- Configuration issues persist after following this guide
- Data corruption or loss
- Security concerns
- Production deployment issues
- Custom integration requirements

### **How to Get Help:**

#### **1. Gather Information:**
```bash
# System information
python --version
pip list | grep -E "(fastapi|pandas|numpy|sqlalchemy)"

# Error logs
tail -50 logs/errors.log

# Configuration
cat config/config.yaml
```

#### **2. Create Minimal Reproduction:**
- Minimal dataset that causes the issue
- Exact steps to reproduce
- Expected vs actual behavior

#### **3. Contact Channels:**
- 📧 **Email**: support@moatmetrics.com
- 🐛 **GitHub Issues**: Include system info and reproduction steps
- 📚 **Documentation**: Check other docs in `/docs` folder
- 💬 **Community**: Join our Discord for peer support

### **Emergency Situations:**

#### **Production Down:**
```bash
# Quick restart
pkill -f python
python main.py

# Check system resources
df -h  # Disk space
free -m  # Memory
top  # CPU usage
```

#### **Data Recovery:**
```bash
# Restore from backup
cp data/moatmetrics.db.backup data/moatmetrics.db

# Or recreate from CSV files
rm data/moatmetrics.db
python main.py
# Re-upload all CSV files in order
```

---

## ✅ **Preventive Measures**

### **Best Practices:**
1. **Regular Backups**: Backup database before major operations
2. **Resource Monitoring**: Monitor disk, memory, and CPU usage
3. **Log Rotation**: Implement log rotation for large deployments
4. **Version Control**: Keep track of configuration changes
5. **Testing**: Test data uploads with small samples first
6. **Documentation**: Document custom configurations

### **Monitoring Checklist:**
- [ ] Database size and growth rate
- [ ] Log file sizes
- [ ] Memory usage patterns
- [ ] API response times
- [ ] Disk space availability
- [ ] Backup integrity

---

**Need more help?** 

Check our other documentation:
- [Architecture Guide](ARCHITECTURE.md) - System design details
- [Challenges & Fixes](CHALLENGES_AND_FIXES.md) - Development issues resolved
- [Quick Start Guide](QUICKSTART.md) - Initial setup instructions
- [API Documentation](API.md) - Complete API reference

**Remember:** Most issues have been encountered and solved before. This troubleshooting guide contains solutions to 95% of common problems. When in doubt, check the logs first! 📝
