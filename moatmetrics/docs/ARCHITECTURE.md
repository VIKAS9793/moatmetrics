# MoatMetrics System Architecture

## 🏗️ **Overview**

MoatMetrics is built on a modular, layered architecture designed for scalability, maintainability, and security. The system follows clean architecture principles with clear separation of concerns between data, business logic, and presentation layers.

## 🎯 **Design Principles**

- **Privacy-First**: All data processing happens locally
- **Explainable AI**: Every decision includes reasoning and confidence
- **Human-in-the-Loop**: Automated governance with human oversight
- **Modularity**: Loosely coupled, highly cohesive components
- **Compliance**: Built-in audit trails and governance
- **Scalability**: Horizontal scaling capabilities

---

## 📊 **High-Level Architecture**

```mermaid
flowchart TB
    subgraph "Client Tier"
        WebApp["🌐 Web Application<br/>(Interactive Docs)"]
        APIClient["📱 API Client<br/>(REST/JSON)"]
    end
    
    subgraph "API Gateway Tier"
        FastAPI["⚡ FastAPI Server<br/>(Python 3.11)"]
        Auth["🔐 Authentication<br/>(Role-Based)"]
        CORS["🌍 CORS<br/>(Cross-Origin)"]
    end
    
    subgraph "Business Logic Tier"
        ETL["🔄 ETL Pipeline<br/>(Data Processing)"]
        Analytics["🧠 Analytics Engine<br/>(ML/AI)"]
        Governance["🛡️ Governance Engine<br/>(Policy & Audit)"]
        Reports["📊 Report Generator<br/>(PDF/CSV)"]
    end
    
    subgraph "Data Tier"
        SQLite[("🗄️ SQLite Database<br/>(ACID Compliant)")]
        Files["📁 File Storage<br/>(CSV/Reports)"]
        Snapshots["📸 Data Snapshots<br/>(Versioning)"]
    end
    
    WebApp --> FastAPI
    APIClient --> FastAPI
    FastAPI --> Auth
    FastAPI --> CORS
    
    Auth --> ETL
    Auth --> Analytics
    Auth --> Governance
    Auth --> Reports
    
    ETL --> SQLite
    Analytics --> SQLite
    Governance --> SQLite
    Reports --> SQLite
    
    ETL --> Files
    Reports --> Files
    ETL --> Snapshots
```

---

## 🔄 **Data Flow Architecture**

```mermaid
flowchart LR
    subgraph "Data Ingestion"
        CSV["📄 CSV Upload"]
        Validation["✅ Schema Validation"]
        Processing["⚙️ Data Processing"]
    end
    
    subgraph "Storage Layer"
        DB[("🗄️ Database")]
        Snapshots["📸 Snapshots"]
    end
    
    subgraph "Analytics Pipeline"
        Compute["🧮 Metrics Computation"]
        Confidence["🎯 Confidence Scoring"]
        SHAP["📊 SHAP Explanations"]
    end
    
    subgraph "Governance Layer"
        Policy["📋 Policy Check"]
        Review["👤 Human Review"]
        Audit["📝 Audit Log"]
    end
    
    subgraph "Output Layer"
        Results["📈 Analytics Results"]
        Reports["📄 Generated Reports"]
        API["🔌 API Response"]
    end
    
    CSV --> Validation
    Validation --> Processing
    Processing --> DB
    Processing --> Snapshots
    
    DB --> Compute
    Compute --> Confidence
    Confidence --> SHAP
    
    SHAP --> Policy
    Policy --> Review
    Review --> Audit
    
    Audit --> Results
    Results --> Reports
    Results --> API
```

---

## 🏛️ **Component Architecture**

### **1. API Layer**

```mermaid
classDiagram
    class FastAPIApp {
        +health_check()
        +upload_file()
        +run_analytics()
        +get_results()
        +generate_report()
    }
    
    class Authentication {
        +get_current_user()
        +check_permissions()
        +verify_role()
    }
    
    class CORSMiddleware {
        +allow_origins()
        +allow_methods()
        +allow_headers()
    }
    
    FastAPIApp --> Authentication
    FastAPIApp --> CORSMiddleware
```

### **2. Business Logic Layer**

```mermaid
classDiagram
    class ETLPipeline {
        +process_file()
        +validate_schema()
        +create_snapshot()
        +save_data()
    }
    
    class AnalyticsEngine {
        +run_analytics()
        +analyze_profitability()
        +analyze_license_efficiency()
        +calculate_confidence()
    }
    
    class PolicyEngine {
        +check_permission()
        +enforce_governance()
        +evaluate_confidence()
        +log_audit_entry()
    }
    
    class ReportGenerator {
        +generate_pdf()
        +generate_csv()
        +create_dashboard()
    }
    
    ETLPipeline --> AnalyticsEngine
    AnalyticsEngine --> PolicyEngine
    PolicyEngine --> ReportGenerator
```

### **3. Data Layer**

```mermaid
erDiagram
    CLIENT {
        int client_id PK
        string name
        string industry
        boolean is_active
        datetime created_at
    }
    
    INVOICE {
        int invoice_id PK
        int client_id FK
        decimal total_amount
        date invoice_date
        string status
    }
    
    TIME_LOG {
        int log_id PK
        int client_id FK
        string staff_name
        decimal hours
        decimal rate
        boolean billable
    }
    
    LICENSE {
        int license_id PK
        int client_id FK
        string product
        int seats_purchased
        int seats_used
        decimal total_cost
    }
    
    ANALYTICS_RESULT {
        int result_id PK
        int client_id FK
        string metric_type
        decimal value
        decimal confidence_score
        boolean requires_review
    }
    
    CLIENT ||--o{ INVOICE : "has"
    CLIENT ||--o{ TIME_LOG : "has"
    CLIENT ||--o{ LICENSE : "has"
    CLIENT ||--o{ ANALYTICS_RESULT : "analyzed"
```

---

## 🔧 **Technical Stack**

### **Backend Framework**
```mermaid
graph LR
    Python["🐍 Python 3.11+"] --> FastAPI["⚡ FastAPI 0.104+"]
    FastAPI --> Uvicorn["🦄 Uvicorn ASGI"]
    Uvicorn --> Pydantic["✅ Pydantic v2"]
```

### **Data Processing**
```mermaid
graph LR
    Pandas["🐼 Pandas"] --> NumPy["🔢 NumPy"]
    NumPy --> ScikitLearn["🤖 Scikit-Learn"]
    ScikitLearn --> SHAP["📊 SHAP"]
```

### **Database & ORM**
```mermaid
graph LR
    SQLite["🗄️ SQLite"] --> SQLAlchemy["🔗 SQLAlchemy ORM"]
    SQLAlchemy --> Alembic["🔄 Alembic Migrations"]
```

---

## 🚀 **Deployment Architecture**

### **Local Development**
```mermaid
flowchart TB
    subgraph "Development Environment"
        Dev["💻 Developer Machine"]
        VEnv["🐍 Python Virtual Env"]
        SQLiteDev[("🗄️ SQLite Dev DB")]
    end
    
    subgraph "Application"
        FastAPIDev["⚡ FastAPI (Debug)"]
        LogsDev["📝 Debug Logs"]
    end
    
    Dev --> VEnv
    VEnv --> FastAPIDev
    FastAPIDev --> SQLiteDev
    FastAPIDev --> LogsDev
```

### **Production Deployment**
```mermaid
flowchart TB
    subgraph "Load Balancer"
        LB["⚖️ Load Balancer<br/>(Nginx/HAProxy)"]
    end
    
    subgraph "Application Servers"
        App1["⚡ FastAPI Instance 1"]
        App2["⚡ FastAPI Instance 2"]
        AppN["⚡ FastAPI Instance N"]
    end
    
    subgraph "Data Layer"
        DB[("🗄️ SQLite Database<br/>(Replicated)")]
        FileStore["📁 Shared File Storage"]
        Backup["💾 Backup Storage"]
    end
    
    subgraph "Monitoring"
        Logs["📊 Centralized Logging"]
        Metrics["📈 Application Metrics"]
        Health["❤️ Health Checks"]
    end
    
    LB --> App1
    LB --> App2
    LB --> AppN
    
    App1 --> DB
    App2 --> DB
    AppN --> DB
    
    App1 --> FileStore
    App2 --> FileStore
    AppN --> FileStore
    
    DB --> Backup
    
    App1 --> Logs
    App2 --> Logs
    AppN --> Logs
    
    App1 --> Metrics
    App2 --> Metrics
    AppN --> Metrics
    
    App1 --> Health
    App2 --> Health
    AppN --> Health
```

---

## 🔐 **Security Architecture**

```mermaid
flowchart TB
    subgraph "Authentication Layer"
        Auth["🔐 Authentication"]
        RBAC["👥 Role-Based Access"]
        Sessions["🎫 Session Management"]
    end
    
    subgraph "Authorization Layer"
        Permissions["🛡️ Permission Checks"]
        Policies["📋 Policy Enforcement"]
        DataGov["🏛️ Data Governance"]
    end
    
    subgraph "Audit Layer"
        AuditLog["📝 Audit Logging"]
        Compliance["✅ Compliance Check"]
        Retention["⏰ Data Retention"]
    end
    
    subgraph "Data Protection"
        Encryption["🔒 Data Encryption"]
        LocalOnly["🏠 Local Processing"]
        Privacy["🔐 Privacy Controls"]
    end
    
    Auth --> RBAC
    RBAC --> Sessions
    
    Sessions --> Permissions
    Permissions --> Policies
    Policies --> DataGov
    
    DataGov --> AuditLog
    AuditLog --> Compliance
    Compliance --> Retention
    
    Retention --> Encryption
    Encryption --> LocalOnly
    LocalOnly --> Privacy
```

---

## 📊 **Analytics Architecture**

```mermaid
flowchart TB
    subgraph "Data Preparation"
        Extract["🔍 Data Extraction"]
        Clean["🧹 Data Cleaning"]
        Transform["🔄 Data Transformation"]
    end
    
    subgraph "Feature Engineering"
        Features["🏗️ Feature Creation"]
        Selection["🎯 Feature Selection"]
        Scaling["📏 Feature Scaling"]
    end
    
    subgraph "Model Computation"
        Profitability["💰 Profitability Model"]
        License["📄 License Efficiency"]
        Resource["👥 Resource Utilization"]
    end
    
    subgraph "Explainability"
        SHAP["📊 SHAP Values"]
        Confidence["🎯 Confidence Score"]
        Explanation["📝 Human Explanation"]
    end
    
    subgraph "Quality Assurance"
        Validation["✅ Result Validation"]
        Review["👤 Human Review"]
        Approval["✅ Approval Workflow"]
    end
    
    Extract --> Clean
    Clean --> Transform
    
    Transform --> Features
    Features --> Selection
    Selection --> Scaling
    
    Scaling --> Profitability
    Scaling --> License
    Scaling --> Resource
    
    Profitability --> SHAP
    License --> SHAP
    Resource --> SHAP
    
    SHAP --> Confidence
    Confidence --> Explanation
    
    Explanation --> Validation
    Validation --> Review
    Review --> Approval
```

---

## 🗂️ **File System Architecture**

```
moatmetrics/
├── 📁 config/                    # Configuration files
│   ├── config.yaml              # Main configuration
│   └── policies/                # Governance policies
│       └── default_policy.json
├── 📁 src/                       # Source code
│   ├── api/                     # FastAPI endpoints
│   ├── analytics/               # Analytics engine
│   ├── etl/                     # ETL pipeline
│   ├── governance/              # Policy engine
│   ├── agent/                   # Report generator
│   └── utils/                   # Shared utilities
├── 📁 data/                      # Data storage
│   ├── raw/                     # Raw CSV files
│   ├── processed/               # Processed data
│   ├── snapshots/               # Data versioning
│   └── moatmetrics.db          # SQLite database
├── 📁 reports/                   # Generated reports
├── 📁 logs/                      # Application logs
├── 📁 docs/                      # Documentation
└── 📁 tests/                     # Test suite
```

---

## 🔄 **State Management**

```mermaid
stateDiagram-v2
    [*] --> DataUpload
    DataUpload --> Validation
    Validation --> Processing : Valid
    Validation --> Error : Invalid
    Processing --> Stored
    Stored --> AnalyticsRequest
    AnalyticsRequest --> Computing
    Computing --> Confident : High Confidence
    Computing --> Review : Low Confidence
    Review --> Approved : Human Approval
    Review --> Rejected : Human Rejection
    Confident --> Results
    Approved --> Results
    Results --> ReportGeneration
    ReportGeneration --> Complete
    Complete --> [*]
    Error --> [*]
    Rejected --> [*]
```

---

## 🧩 **Integration Architecture**

```mermaid
flowchart TB
    subgraph "External Integrations"
        FileSystem["📁 File System<br/>(CSV/Excel)"]
        Email["📧 Email Notifications<br/>(SMTP)"]
        Backup["💾 Backup Systems<br/>(Cloud/Local)"]
    end
    
    subgraph "MoatMetrics Core"
        API["⚡ FastAPI Core"]
        ETL["🔄 ETL Engine"]
        Analytics["🧠 Analytics"]
        Reports["📊 Reports"]
    end
    
    subgraph "Monitoring Integrations"
        Prometheus["📈 Prometheus<br/>(Metrics)"]
        Grafana["📊 Grafana<br/>(Dashboards)"]
        AlertManager["🚨 Alert Manager<br/>(Notifications)"]
    end
    
    FileSystem --> ETL
    ETL --> Analytics
    Analytics --> Reports
    Reports --> Email
    
    API --> Backup
    
    API --> Prometheus
    Prometheus --> Grafana
    Prometheus --> AlertManager
```

---

## 🎯 **Performance Considerations**

### **Database Optimization**
- Proper indexing on frequently queried columns
- Connection pooling for concurrent requests
- Query optimization using SQLAlchemy best practices

### **Caching Strategy**
- In-memory caching for frequently accessed data
- Result caching for expensive analytics computations
- File-based caching for generated reports

### **Scalability**
- Horizontal scaling through multiple FastAPI instances
- Database read replicas for analytics queries
- Async processing for long-running operations

### **Memory Management**
- Streaming processing for large CSV files
- Garbage collection optimization for ML operations
- Memory-efficient data structures

---

## 🔧 **Configuration Management**

```mermaid
flowchart TB
    subgraph "Configuration Sources"
        YAML["📄 config.yaml<br/>(Default Settings)"]
        ENV["🌍 Environment Variables<br/>(Runtime Overrides)"]
        CLI["⌨️ Command Line Args<br/>(Execution Parameters)"]
    end
    
    subgraph "Configuration Loader"
        Loader["⚙️ Config Loader<br/>(Priority Resolution)"]
        Validator["✅ Config Validator<br/>(Schema Check)"]
    end
    
    subgraph "Application Components"
        Database["🗄️ Database Config"]
        API["⚡ API Config"]
        Analytics["🧠 Analytics Config"]
        Logging["📝 Logging Config"]
    end
    
    YAML --> Loader
    ENV --> Loader
    CLI --> Loader
    
    Loader --> Validator
    
    Validator --> Database
    Validator --> API
    Validator --> Analytics
    Validator --> Logging
```

This architecture ensures MoatMetrics is scalable, maintainable, secure, and compliant with enterprise requirements while maintaining the privacy-first approach that sets it apart from cloud-based alternatives.
