# MoatMetrics

<div align="center">
  <h3>🔒 Privacy-First Analytics Platform for MSPs</h3>
  <p><strong>Statistical Analytics • Human-in-the-Loop • Complete Data Control</strong></p>
  
  ![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
  ![Python](https://img.shields.io/badge/Python-3.11+-blue)
  ![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)
  ![SQLite](https://img.shields.io/badge/Database-SQLite-lightblue)
  ![License](https://img.shields.io/badge/License-MIT-yellow)
</div>

---

## 📋 Table of Contents

- [🚀 Project Status](#-project-status)
- [🎯 Overview](#-overview)
- [🏗️ System Architecture](#️-system-architecture)
- [⚡ Quick Start](#-quick-start)
- [📸 Screenshots & Visual Overview](#-screenshots--visual-overview)
- [📊 Core Features](#-core-features)
- [📈 Analytics Capabilities](#-analytics-capabilities)
- [🛡️ Security & Compliance](#️-security--compliance)
- [📚 Documentation](#-documentation)
- [🎯 Use Cases](#-use-cases)
- [🔮 Future Roadmap](#-future-roadmap)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [🙋‍♂️ Support](#️-support)
- [👨‍💼 Contact](#-contact)

---

## 🚀 **Project Status: PRODUCTION READY** ✅

**MoatMetrics MVP is now 100% functional and production-ready!** All core features have been implemented, tested, and verified working end-to-end.

### **✅ Completed Features:**
- [x] **Data Pipeline**: CSV upload → validation → processing → storage
- [x] **Analytics Engine**: Profitability, license efficiency, resource utilization
- [x] **AI Analytics**: Advanced NL Analytics with TinyLlama integration
- [x] **Statistical Analytics**: Rule-based explanations with confidence scoring
- [x] **Human-in-the-Loop**: Automated review workflow for low-confidence results
- [x] **Governance**: Role-based access, audit trails, compliance reporting
- [x] **REST API**: Complete FastAPI implementation with interactive docs
- [x] **Database**: SQLite with proper session management and transactions
- [x] **Repository Structure**: Professional organization with comprehensive testing
- [x] **AI Memory Management**: Hardware-aware model selection and optimization
- [x] **Security Framework**: Advanced threat detection and privacy protection

---

## 🎯 **Overview**

MoatMetrics is a comprehensive analytics platform designed specifically for Managed Service Providers (MSPs) who need to analyze client profitability, license efficiency, and resource utilization while maintaining complete data privacy and control.

### **🔑 Key Differentiators:**
- **🔒 Privacy-First**: All processing happens locally - zero data leaves your environment
- **📊 Statistical Analytics**: Every result includes business rule explanations and confidence scores
- **👥 Human-in-the-Loop**: Automated governance with human oversight for critical decisions
- **📊 MSP-Specific**: Purpose-built analytics for client profitability and resource optimization
- **🛡️ Enterprise-Grade**: Audit trails, compliance reporting, and role-based access control

---

## 🏗️ **System Architecture**

```mermaid
flowchart TB
    subgraph "Data Layer"
        CSV["📄 CSV Files"]
        DB[("🗃️ SQLite Database")]
    end
    
    subgraph "Processing Layer"
        ETL["🔄 ETL Pipeline"]
        Analytics["🧠 Analytics Engine"]
        AI["🤖 AI Analytics (TinyLlama)"]
        Governance["🛡️ Policy Engine"]
    end
    
    subgraph "API Layer"
        FastAPI["⚡ FastAPI Server"]
        Auth["🔐 Authentication"]
    end
    
    subgraph "Client Layer"
        WebUI["🌐 Web Interface"]
        API_Client["📱 API Client"]
    end
    
    CSV --> ETL
    ETL --> DB
    DB --> Analytics
    DB --> AI
    Analytics --> Governance
    AI --> Governance
    Governance --> FastAPI
    FastAPI --> Auth
    Auth --> WebUI
    Auth --> API_Client
```

---

## ⚡ **Quick Start**

### **Prerequisites**
- Python 3.11 or higher
- Git
- 2GB RAM minimum
- 1GB disk space

### **Installation**

```bash
# 1. Clone the repository
git clone https://github.com/VIKAS9793/moatmetrics.git
cd moatmetrics

# 2. Create virtual environment
python -m venv moatmetrics_env

# 3. Activate virtual environment
# Windows:
moatmetrics_env\Scripts\activate
# macOS/Linux:
source moatmetrics_env/bin/activate

# 4. Install dependencies
cd moatmetrics
pip install -r requirements.txt

# Note: The requirements.txt now includes ALL dependencies (71 packages)
# No additional installations needed - everything is included!

# 5. Start the application
python main.py
```

### **Verify Installation**

```bash
# Check health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","timestamp":"2025-09-04T15:55:30Z","version":"1.0.0-prototype"}
```

🎉 **Success!** MoatMetrics is now running at:
- **🌐 Web Interface**: http://localhost:8000/docs
- **📚 API Documentation**: http://localhost:8000/redoc
- **❤️ Health Check**: http://localhost:8000/health

---

## 📸 **Screenshots & Visual Overview**

### **🔐 Authentication & Access Control**
![Login Panel](https://github.com/VIKAS9793/moatmetrics/blob/main/moatmetrics/image/assets/Login%20panel.png)
*Secure login with role-based access control*

### **📊 Main Dashboard**
![Main Dashboard](https://github.com/VIKAS9793/moatmetrics/blob/main/moatmetrics/image/assets/Main%20UI%20Dashboard.png)
*Comprehensive analytics dashboard with key metrics*

![Dashboard Alternative View](https://github.com/VIKAS9793/moatmetrics/blob/main/moatmetrics/image/assets/Main%20UI%20Dashboard%202.png)
*Alternative dashboard layout with detailed insights*

### **👨‍💼 Administration Panel**
![Admin Panel](https://github.com/VIKAS9793/moatmetrics/blob/main/moatmetrics/image/assets/Admin%20Panel.png)
*Administrative controls for user and system management*

### **📤 Data Upload Interface**
![Data Upload UI](https://github.com/VIKAS9793/moatmetrics/blob/main/moatmetrics/image/assets/Data%20Upload%20UI.png)
*Intuitive data upload with validation and preview*

![Data Upload UI 2](https://github.com/VIKAS9793/moatmetrics/blob/main/moatmetrics/image/assets/Data%20Upload%20UI%202.png)
*Advanced upload features with error handling*

![Data Upload UI 3](https://github.com/VIKAS9793/moatmetrics/blob/main/moatmetrics/image/assets/Data%20Upload%20UI%203.png)
*Bulk data processing with progress tracking*

### **🔧 API Documentation**
![Swagger UI](https://github.com/VIKAS9793/moatmetrics/blob/main/moatmetrics/image/assets/Swagger%20UI%201.png)
*Interactive API documentation with FastAPI*

![Swagger UI 2](https://github.com/VIKAS9793/moatmetrics/blob/main/moatmetrics/image/assets/Swagger%20UI%202.png)
*Detailed endpoint documentation and testing*

![Swagger UI 3](https://github.com/VIKAS9793/moatmetrics/blob/main/moatmetrics/image/assets/Swagger%20UI%203.png)
*Complete API reference with request/response examples*

---

## 📊 **Core Features**

### **1. Data Processing Pipeline**
- **📁 Multi-format Support**: CSV, Excel files
- **🔍 Schema Validation**: Automatic data quality checks
- **⚡ Incremental Processing**: Handle large datasets efficiently
- **📸 Data Snapshots**: Version control for all uploads

### **2. Statistical Analytics**
- **💰 Profitability Analysis**: Revenue vs. costs by client
- **📄 License Efficiency**: Utilization rates and waste detection
- **👥 Resource Utilization**: Staff productivity and capacity planning
- **📊 Statistical Methods**: Descriptive analytics and business insights

### **3. Advanced AI Analytics**
- **🤖 Natural Language Processing**: Query your data using natural language
- **🧠 TinyLlama Integration**: Hardware-aware AI model selection and optimization
- **🎯 Confidence Scoring**: Every metric includes reliability assessment
- **📋 AI-Generated Explanations**: Intelligent business insights and recommendations
- **⚡ Memory Management**: Automatic model loading and resource optimization
- **🔍 Transparency**: Full visibility into calculation methods and AI reasoning

### **4. Human-in-the-Loop Governance**
- **⚠️ Automatic Review**: Low-confidence results flagged for human review
- **👤 Approval Workflows**: Configurable approval chains
- **📋 Audit Trails**: Complete history of all decisions and changes

---

## 📈 **Analytics Capabilities**

| **Metric Type** | **Description** | **Key Insights** |
|---|---|---|
| **💰 Profitability** | Client revenue vs. labor costs | Profit margins, cost optimization opportunities |
| **📄 License Efficiency** | Software license utilization | Waste reduction, cost savings potential |
| **👥 Resource Utilization** | Staff productivity analysis | Capacity planning, workload optimization |
| **📊 Spend Analysis** | Budget and spending patterns | Cost trends, budget variance analysis |
| **🤖 AI Query Processing** | Natural language analytics queries | Intelligent insights, recommendations, confidence scoring |
| **🧠 Memory Management** | Hardware-aware AI optimization | Automatic model selection, resource efficiency |

---

## 🛡️ **Security & Compliance**

- **🔒 Local Processing**: All data stays on your infrastructure
- **🔐 Role-Based Access**: Granular permissions (Admin, Analyst, Viewer)
- **📋 Audit Logging**: Complete activity tracking
- **✅ Compliance Ready**: GDPR, HIPAA, SOC2 compatible architecture
- **🛡️ Data Governance**: Automated policy enforcement

---

## 📁 **Project Structure**

MoatMetrics follows a clean, professional structure:

```
moatmetrics/
├── 📁 docs/                    # Complete documentation suite (25+ guides)
├── 💻 src/                     # Source code (modular architecture)
│   ├── ai/                      # AI/ML components (TinyLlama, NL Analytics)
│   ├── api/                     # FastAPI endpoints and routes
│   ├── analytics/               # Core analytics engine
│   ├── etl/                     # Data processing pipeline
│   └── utils/                   # Shared utilities and helpers
├── 🧪 tests/                   # Comprehensive test suite
├── 🔧 scripts/                 # Utility scripts (database, data generation)
├── 📊 data/                    # Data storage (SQLite, CSV files)
├── ⚙️ config/                  # Configuration files
└── 📄 main.py                  # Application entry point
```

**Key Improvements**:
- ✅ Professional Python project structure
- ✅ Clean separation of concerns
- ✅ Comprehensive testing with 100% pass rate
- ✅ AI components properly organized
- ✅ Documentation consolidated and cross-referenced

---

## 📚 **Documentation**
|| **Document** | **Description** |
|---|---|
| [🏗️ Architecture Guide](https://github.com/VIKAS9793/moatmetrics/blob/main/moatmetrics/docs/ARCHITECTURE.md) | System design and technical architecture |
| [📜 PRD](https://github.com/VIKAS9793/moatmetrics/blob/main/moatmetrics/docs/PRD.md) | Product requirements and specifications |
| [🔧 Technical Spec](https://github.com/VIKAS9793/moatmetrics/blob/main/moatmetrics/docs/TECHNICAL_SPEC.md) | Detailed technical specifications |
| [📘 User Guide](https://github.com/VIKAS9793/moatmetrics/blob/main/moatmetrics/docs/USER_GUIDE.md) | End-user documentation |
| [🔐 Security Framework](https://github.com/VIKAS9793/moatmetrics/blob/main/moatmetrics/docs/SECURITY_FRAMEWORK.md) | Security policies and controls |
| [📊 Analytics Spec](https://github.com/VIKAS9793/moatmetrics/blob/main/moatmetrics/docs/ANALYTICS_SPEC.md) | Analytics methodology and metrics |
| [📈 Project Status](https://github.com/VIKAS9793/moatmetrics/blob/main/moatmetrics/docs/PROJECT_STATUS.md) | Current development status and roadmap |
| [🚀 Quick Start](https://github.com/VIKAS9793/moatmetrics/blob/main/moatmetrics/docs/QUICKSTART.md) | Complete 5-minute setup guide |
| [👨‍💻 MVP Quick Start](https://github.com/VIKAS9793/moatmetrics/blob/main/moatmetrics/QUICKSTART.md) | Technical MVP setup guide |
| [👨‍💼 Admin Guide](https://github.com/VIKAS9793/moatmetrics/blob/main/moatmetrics/docs/ADMIN_GUIDE.md) | Administrator documentation |
| [🏢 MSP Guide](https://github.com/VIKAS9793/moatmetrics/blob/main/moatmetrics/docs/MSP_GUIDE.md) | MSP-specific usage guide |
| [📋 API Documentation](https://github.com/VIKAS9793/moatmetrics/blob/main/moatmetrics/docs/API.md) | API reference and examples |
| [🚀 Deployment Guide](https://github.com/VIKAS9793/moatmetrics/blob/main/moatmetrics/docs/DEPLOYMENT.md) | Production deployment instructions |
| [🔧 Troubleshooting](https://github.com/VIKAS9793/moatmetrics/blob/main/moatmetrics/docs/TROUBLESHOOTING.md) | Common issues and solutions |
| [📊 Business Case](https://github.com/VIKAS9793/moatmetrics/blob/main/moatmetrics/docs/BUSINESS_CASE.md) | Business justification and ROI analysis |
| [🗺️ Roadmap](https://github.com/VIKAS9793/moatmetrics/blob/main/moatmetrics/docs/ROADMAP.md) | Future development plans |
| [🔗 Integration Guide](https://github.com/VIKAS9793/moatmetrics/blob/main/moatmetrics/docs/INTEGRATION_GUIDE.md) | Third-party integration instructions |
| [📚 Getting Started](https://github.com/VIKAS9793/moatmetrics/blob/main/moatmetrics/docs/GETTING_STARTED.md) | Detailed setup guide |
| [🔧 Challenges & Fixes](https://github.com/VIKAS9793/moatmetrics/blob/main/moatmetrics/docs/CHALLENGES_AND_FIXES.md) | Known issues and resolutions |
| [📁 Project Structure](https://github.com/VIKAS9793/moatmetrics/blob/main/moatmetrics/docs/PROJECT_STRUCTURE.md) | Complete directory organization guide |
| [🧪 Test Report](https://github.com/VIKAS9793/moatmetrics/blob/main/moatmetrics/docs/RESTRUCTURE_TEST_REPORT.md) | Comprehensive testing validation report |
| [📸 Screenshots Gallery](https://github.com/VIKAS9793/moatmetrics/tree/main/moatmetrics/image/assets) | UI screenshots and visual assets |

---

## 🎯 **Use Cases**

### **For MSP Executives**
- 📊 Client profitability analysis
- 💡 Strategic decision making
- 📈 Business growth insights

### **For Operations Managers**
- 👥 Resource optimization
- 📄 License cost management
- ⚡ Process efficiency improvements

### **For Financial Analysts**
- 💰 Cost center analysis
- 📋 Budget planning and forecasting
- 🔍 Variance analysis

---

## 🔮 **Future Roadmap**

### **Phase 2: Enhanced Features (Q1 2026)**
- ✅ **Natural Language Analytics**: Advanced NL processing with TinyLlama (COMPLETED)
- ✅ **AI Memory Management**: Hardware-aware model optimization (COMPLETED)
- ✅ **Advanced Security Framework**: Threat detection and privacy protection (COMPLETED)
- 📊 **Advanced Visualizations**: Interactive dashboards and reports
- 🔗 **PSA Integrations**: ConnectWise, Autotask, ServiceNow connectivity
- 🔮 **SHAP Integration**: Explainable AI with SHAP values

### **Phase 3: Enterprise Platform (Q2 2026)**
- 🏢 **Multi-Tenancy**: Organization management and data isolation
- 🔐 **Advanced Security**: SSO, advanced RBAC, end-to-end encryption
- 📱 **Mobile Apps**: iOS and Android applications

### **Phase 4: AI Innovation (Q3 2026)**
- 🧠 **Deep Learning**: Advanced pattern recognition
- 💬 **Natural Language**: Chat-based analytics interface
- 🤖 **AutoML**: Self-improving predictive models

---

## 🤝 **Contributing**

We welcome contributions! Please see our [Contribution Guidelines](https://github.com/VIKAS9793/moatmetrics/blob/main/CONTRIBUTING.md) and [Code of Conduct](https://github.com/VIKAS9793/moatmetrics/blob/main/CODE_OF_CONDUCT.md) for details on how to contribute to this project. Also, check out our [Changelog](https://github.com/VIKAS9793/moatmetrics/blob/main/CHANGELOG.md) to see what's new and what's coming next.

---

## 📄 **License**

MIT License - see [LICENSE](https://github.com/VIKAS9793/moatmetrics/blob/main/moatmetrics/LICENSE) file for details.

---

## 🙋‍♂️ **Support**

- 📧 **Email**: support@moatmetrics.com
- 💬 **Discord**: [MoatMetrics Community](https://discord.gg/moatmetrics)
- 🛠️ **Issues**: [GitHub Issues](https://github.com/VIKAS9793/moatmetrics/issues)
- 📖 **Documentation**: Complete guides available in `/docs`

---

<div align="center">
  <p><strong>Built with ❤️ for the MSP community</strong></p>
  <p>⭐ Star us on GitHub if MoatMetrics helps your business!</p>
  
**Current Status: Production Ready | Testing: 100% Pass Rate | Next: Beta Customer Acquisition**

### **🧪 Recent Validation (Sept 2025)**
- ✅ **Complete Restructuring**: Professional repository organization
- ✅ **Comprehensive Testing**: All imports, API, AI components validated
- ✅ **AI Integration**: TinyLlama model successfully processing queries
- ✅ **Performance Verified**: 30-80s query processing with confidence scoring
- ✅ **Database Operations**: All CRUD operations and migrations working
- ✅ **API Endpoints**: FastAPI fully operational with interactive docs
</div>

## 👨‍💼 Contact

- **Product Owner**: VIKAS SAHANI
- **Email**: vikassahani17@gmail.com
- **LinkedIn**: [linkedin.com/in/vikas-sahani-727420358](https://www.linkedin.com/in/vikas-sahani-727420358)
- **GitHub**: [github.com/VIKAS9793](https://github.com/VIKAS9793)