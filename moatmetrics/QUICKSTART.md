# 🚀 MoatMetrics MVP - Quick Start Guide

## Overview
MoatMetrics is a **privacy-first, offline, explainable analytics platform** for MSPs (Managed Service Providers). This MVP demonstrates:
- ✅ **100% Offline Operation** - No cloud dependencies
- ✅ **Explainable AI** - SHAP values for all insights
- ✅ **Data Governance** - Role-based access, audit trails
- ✅ **Human-in-the-Loop** - Review triggers for low-confidence insights
- ✅ **Comprehensive Reporting** - PDF, CSV, JSON formats

## 🎯 Quick Setup (5 minutes)

### 1. Prerequisites
- Python 3.11 or higher
- Windows PowerShell (for Windows users)

### 2. Install Dependencies
```bash
cd moatmetrics
pip install -r requirements.txt
```

### 3. Generate Sample Data
```bash
python generate_sample_data.py
```

This creates sample CSV files in `moatmetrics/data/raw/`:
- `clients.csv` - 10 sample clients
- `invoices.csv` - 50 invoices with line items
- `time_logs.csv` - 200 time tracking entries
- `licenses.csv` - 30 software licenses with utilization data

### 4. Start the API Server
```bash
python main.py
```

The server will start at: **http://127.0.0.1:8000**

## 📊 Key Endpoints

### Interactive API Documentation
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

### Core Functionality

#### 1. Upload Data
```bash
POST /api/upload/{data_type}
```
Upload CSV files (clients, invoices, time_logs, licenses)

#### 2. Run Analytics
```bash
POST /api/analytics/run
```
Compute profitability, license efficiency, and other metrics with SHAP explanations

#### 3. Generate Reports
```bash
POST /api/reports/generate
```
Create PDF/CSV/JSON reports with audit trails

#### 4. Check Governance
```bash
GET /api/governance/approvals/pending
```
Review low-confidence insights requiring human approval

## 🎮 Demo Workflow

### Step 1: Upload Sample Data
Use the Swagger UI at http://127.0.0.1:8000/docs:

1. Navigate to `POST /api/upload/{data_type}`
2. Upload each CSV file:
   - Set `data_type` to "clients" and upload `clients.csv`
   - Repeat for invoices, time_logs, and licenses

### Step 2: Run Analytics
1. Navigate to `POST /api/analytics/run`
2. Click "Try it out"
3. Use this request body:
```json
{
  "metric_types": ["profitability", "license_efficiency"],
  "include_explanations": true,
  "confidence_threshold": 0.7
}
```

### Step 3: Review Results
1. Navigate to `GET /api/analytics/results`
2. View computed metrics with:
   - Confidence scores
   - SHAP explanations
   - Actionable recommendations

### Step 4: Generate Report
1. Navigate to `POST /api/reports/generate`
2. Use request body:
```json
{
  "report_type": "summary",
  "format": "pdf",
  "include_audit_trail": true,
  "include_explanations": true
}
```
3. Download the generated report from `moatmetrics/reports/`

## 🔍 Key Features Demonstrated

### 1. **Explainable AI**
Every analytics result includes:
- Confidence score (0-1)
- SHAP values showing feature importance
- Human-readable explanations
- Actionable recommendations

### 2. **Data Quality Assessment**
The system automatically:
- Detects missing fields
- Identifies outliers
- Flags duplicates
- Assigns confidence scores

### 3. **Governance & Compliance**
- **Role-based access**: Admin, Analyst, Viewer roles
- **Audit logging**: Every action is tracked
- **Human-in-the-loop**: Low confidence triggers review
- **Compliance checks**: GDPR, HIPAA, SOC2

### 4. **Ambiguity Handling**
- Metrics with confidence < 0.5 are marked "ambiguous"
- Automatic escalation for human review
- Approval workflows for sensitive actions

## 📁 Project Structure

```
moatmetrics/
├── src/
│   ├── etl/           # Data ingestion & validation
│   ├── analytics/     # Analytics engine with SHAP
│   ├── api/           # FastAPI endpoints
│   ├── governance/    # Policy enforcement
│   ├── agent/         # Orchestration & reporting
│   └── utils/         # Database, schemas, config
├── data/
│   ├── raw/           # Uploaded CSV files
│   ├── processed/     # Normalized data
│   └── snapshots/     # Data versioning
├── reports/           # Generated reports
├── config/
│   └── policies/      # Governance policies
└── logs/             # Application logs
```

## 🔧 Configuration

Edit `config/config.yaml` to customize:
- Analytics thresholds
- Governance policies
- Report settings
- API configuration

Edit `config/policies/default_policy.json` for:
- Role permissions
- Compliance frameworks
- Approval workflows

## 🎯 Use Cases Demonstrated

1. **Client Profitability Analysis**
   - Revenue vs costs per client
   - Profit margins with confidence scores
   - Recommendations for low-margin clients

2. **License Optimization**
   - Identifies underutilized licenses (<50% usage)
   - Calculates waste in dollars
   - Suggests consolidation opportunities

3. **Resource Utilization**
   - Staff utilization rates
   - Billable vs non-billable hours
   - Capacity planning insights

4. **Spend Analysis**
   - Monthly spending trends
   - Active vs inactive license costs
   - Budget optimization recommendations

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're in the `moatmetrics` directory and Python 3.11+ is installed
2. **Port Already in Use**: Change port in `config/config.yaml`
3. **File Not Found**: Run `generate_sample_data.py` first
4. **Database Errors**: Delete `data/moatmetrics.db` and restart

### Logs
Check `logs/` directory for:
- `moatmetrics_YYYY-MM-DD.log` - Application logs
- `errors_YYYY-MM-DD.log` - Error logs with stack traces

## 📚 Next Steps

### For Production:
1. Replace SQLite with PostgreSQL
2. Add authentication (JWT tokens implemented)
3. Deploy with Docker/Kubernetes
4. Add frontend dashboard (React/Next.js ready)
5. Enhance SHAP with more ML models
6. Add real-time monitoring

### For Development:
1. Run tests: `pytest tests/`
2. Format code: `black src/`
3. Type checking: `mypy src/`
4. Linting: `flake8 src/`

## 🤝 Support

For questions or issues:
1. Check the logs in `logs/` directory
2. Review API docs at `/docs`
3. Verify configuration in `config/`

---

**Remember**: This is a prototype for demonstration. Production deployment requires additional security hardening, performance optimization, and infrastructure setup.

## 🎉 Congratulations!
You now have a fully functional MoatMetrics MVP showcasing:
- Privacy-first design (100% offline)
- Explainable AI with confidence scoring
- Comprehensive governance and compliance
- Automated analytics and reporting

Enjoy exploring the platform!
