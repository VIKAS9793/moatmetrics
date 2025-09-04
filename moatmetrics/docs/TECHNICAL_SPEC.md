# Technical Specifications

## 🏗️ **MoatMetrics Technical Architecture Specification**

Detailed technical documentation for developers and system architects covering module interfaces, data schemas, configuration management, and system requirements.

**Document Version**: 1.0.0  
**Last Updated**: September 4, 2025  
**Target Audience**: Software Architects, Senior Developers, DevOps Engineers

---

## 📋 **System Overview**

### **Architecture Principles**
- **Modular Design**: Clear separation of concerns with independent modules
- **Type Safety**: Comprehensive Python type hints and Pydantic validation
- **Configuration-Driven**: YAML and environment variable configuration
- **Database Agnostic**: SQLite for development, PostgreSQL for production
- **API-First**: RESTful API with OpenAPI documentation

### **Technology Stack**

| **Component** | **Technology** | **Version** | **Purpose** |
|---|---|---|---|
| **Runtime** | Python | 3.11+ | Core application platform |
| **Web Framework** | FastAPI | 0.104+ | REST API and async support |
| **Database ORM** | SQLAlchemy | 2.0+ | Database abstraction layer |
| **Validation** | Pydantic | 2.0+ | Data validation and serialization |
| **Logging** | Loguru | 0.7+ | Structured logging |
| **Configuration** | PyYAML | 6.0+ | Configuration management |
| **Analytics** | Pandas, NumPy | Latest | Data processing |

---

## 🗂️ **Module Architecture**

### **Core Modules Structure**

```
src/
├── api/                    # REST API layer
│   ├── __init__.py
│   ├── main.py            # FastAPI application
│   ├── routers/           # API route handlers
│   └── middleware/        # Request/response middleware
├── services/              # Business logic layer
│   ├── __init__.py
│   ├── analytics.py       # Analytics computation
│   ├── data_service.py    # Data management
│   └── governance.py      # Review and approval workflows
├── db/                    # Data access layer
│   ├── __init__.py
│   ├── database.py        # Database connection and sessions
│   ├── models.py          # SQLAlchemy ORM models
│   └── repositories/      # Data access patterns
├── config/                # Configuration management
│   ├── __init__.py
│   ├── config.py          # Configuration classes
│   └── settings.py        # Application settings
├── schemas/               # Pydantic data models
│   ├── __init__.py
│   ├── request_models.py  # API request schemas
│   └── response_models.py # API response schemas
└── utils/                 # Utility functions
    ├── __init__.py
    ├── logging.py         # Logging configuration
    └── validators.py      # Custom validation functions
```

### **Module Dependencies**

```mermaid
flowchart TD
    API[API Layer] --> Services[Services Layer]
    API --> Schemas[Schemas]
    Services --> DB[Database Layer]
    Services --> Config[Configuration]
    DB --> Models[Models]
    Config --> Utils[Utilities]
    Utils --> Logging[Logging]
```

---

## 🔧 **Module Interfaces**

### **1. Analytics Service Interface**

```python
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session

class AnalyticsService:
    """
    Core analytics computation service
    """
    
    def analyze_profitability(
        self,
        session: Session,
        client_ids: Optional[List[int]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        include_explanations: bool = True
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculate client profitability metrics
        
        Args:
            session: Database session
            client_ids: Specific clients to analyze (optional)
            start_date: Analysis period start (optional)
            end_date: Analysis period end (optional)
            include_explanations: Include human-readable explanations
            
        Returns:
            Dictionary with client profitability results
            
        Raises:
            AnalyticsError: When insufficient data or computation fails
        """
        
    def analyze_license_efficiency(
        self,
        session: Session,
        client_ids: Optional[List[int]] = None,
        product_filters: Optional[List[str]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculate license utilization and waste metrics
        """
        
    def analyze_resource_utilization(
        self,
        session: Session,
        staff_names: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculate staff utilization and productivity metrics
        """
        
    def _calculate_confidence_score(
        self,
        features: pd.DataFrame,
        target_value: float,
        metric_type: str
    ) -> Tuple[float, str]:
        """
        Calculate heuristic confidence score for results
        
        Returns:
            Tuple of (confidence_score, explanation)
        """
```

### **2. Data Service Interface**

```python
from typing import Dict, List, Optional, Union
from pandas import DataFrame
from fastapi import UploadFile

class DataService:
    """
    Data ingestion and management service
    """
    
    def upload_csv_data(
        self,
        session: Session,
        file: UploadFile,
        data_type: str,
        validate_schema: bool = True,
        create_snapshot: bool = True
    ) -> Dict[str, Any]:
        """
        Process and store CSV data uploads
        
        Args:
            session: Database session
            file: Uploaded file object
            data_type: Type of data (clients, invoices, time_logs, licenses)
            validate_schema: Perform schema validation
            create_snapshot: Create data snapshot for versioning
            
        Returns:
            Upload result summary with validation details
            
        Raises:
            ValidationError: Schema validation fails
            DataIntegrityError: Foreign key constraints violated
        """
        
    def get_data_quality_metrics(
        self,
        session: Session,
        data_type: str
    ) -> Dict[str, Union[float, int, str]]:
        """
        Calculate data quality metrics for uploaded data
        """
        
    def create_data_snapshot(
        self,
        session: Session,
        data_type: str,
        snapshot_name: Optional[str] = None
    ) -> str:
        """
        Create versioned snapshot of current data state
        """
```

### **3. Governance Service Interface**

```python
from enum import Enum
from typing import List, Optional, Dict, Any

class ReviewStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class GovernanceService:
    """
    Human-in-the-loop review and governance workflows
    """
    
    def create_approval_request(
        self,
        session: Session,
        analysis_result: Dict[str, Any],
        reason: str,
        confidence_score: float
    ) -> str:
        """
        Create approval request for low-confidence results
        """
        
    def process_approval(
        self,
        session: Session,
        request_id: str,
        status: ReviewStatus,
        reviewer_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process approval or rejection of flagged results
        """
        
    def get_audit_trail(
        self,
        session: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve audit trail for compliance and monitoring
        """
```

---

## 📊 **Data Models & Schemas**

### **Database Models (SQLAlchemy)**

#### **Client Model**
```python
from sqlalchemy import Column, Integer, String, Boolean, Numeric, DateTime
from sqlalchemy.sql import func
from src.db.database import Base

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    client_name = Column(String(255), unique=True, nullable=False, index=True)
    industry = Column(String(100), nullable=True)
    status = Column(String(20), nullable=False, default="Active")
    contract_value = Column(Numeric(15, 2), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    invoices = relationship("Invoice", back_populates="client")
    time_logs = relationship("TimeLog", back_populates="client") 
    licenses = relationship("License", back_populates="client")
```

#### **Invoice Model**
```python
class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_id = Column(String(100), unique=True, nullable=False)
    client_name = Column(String(255), ForeignKey("clients.client_name"), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    date = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    client = relationship("Client", back_populates="invoices")
    
    # Indexes
    __table_args__ = (
        Index("idx_invoices_client_date", "client_name", "date"),
        Index("idx_invoices_status", "status"),
    )
```

#### **Time Log Model**
```python
class TimeLog(Base):
    __tablename__ = "time_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    staff_name = Column(String(255), nullable=False)
    client_name = Column(String(255), ForeignKey("clients.client_name"), nullable=False)
    hours = Column(Numeric(5, 2), nullable=False)
    rate = Column(Numeric(8, 2), nullable=False)
    billable = Column(Boolean, nullable=False, default=True)
    date = Column(DateTime, nullable=False)
    project = Column(String(255), nullable=True)
    task_description = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    client = relationship("Client", back_populates="time_logs")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("hours >= 0 AND hours <= 24", name="valid_hours"),
        CheckConstraint("rate >= 0", name="positive_rate"),
        Index("idx_time_logs_client_date", "client_name", "date"),
        Index("idx_time_logs_staff_date", "staff_name", "date"),
    )
```

#### **License Model**
```python
class License(Base):
    __tablename__ = "licenses"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    client_name = Column(String(255), ForeignKey("clients.client_name"), nullable=False)
    product_name = Column(String(255), nullable=False)
    vendor = Column(String(255), nullable=True)
    seats_purchased = Column(Integer, nullable=False)
    seats_used = Column(Integer, nullable=False)
    cost_per_seat = Column(Numeric(8, 2), nullable=False)
    status = Column(String(20), nullable=False, default="Active")
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    client = relationship("Client", back_populates="licenses")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("seats_purchased > 0", name="positive_seats_purchased"),
        CheckConstraint("seats_used >= 0", name="non_negative_seats_used"),
        CheckConstraint("seats_used <= seats_purchased", name="logical_seat_usage"),
        CheckConstraint("cost_per_seat >= 0", name="positive_cost"),
        Index("idx_licenses_client_product", "client_name", "product_name"),
    )
```

### **API Schemas (Pydantic)**

#### **Request Models**
```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Union
from datetime import datetime
from enum import Enum

class DataType(str, Enum):
    CLIENTS = "clients"
    INVOICES = "invoices"
    TIME_LOGS = "time_logs"
    LICENSES = "licenses"

class AnalyticsRequest(BaseModel):
    metric_types: List[str] = Field(
        default=["profitability"],
        description="Types of analytics to run"
    )
    client_ids: Optional[List[int]] = Field(
        default=None,
        description="Specific client IDs to analyze"
    )
    start_date: Optional[datetime] = Field(
        default=None,
        description="Analysis period start date"
    )
    end_date: Optional[datetime] = Field(
        default=None,
        description="Analysis period end date"
    )
    include_explanations: bool = Field(
        default=True,
        description="Include human-readable explanations"
    )
    confidence_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum confidence score threshold"
    )
    
    @validator('metric_types')
    def validate_metric_types(cls, v):
        valid_types = {"profitability", "license_efficiency", "resource_utilization"}
        for metric_type in v:
            if metric_type not in valid_types:
                raise ValueError(f"Invalid metric type: {metric_type}")
        return v
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        if 'start_date' in values and values['start_date'] and v:
            if v < values['start_date']:
                raise ValueError("end_date must be after start_date")
        return v

class ClientData(BaseModel):
    client_name: str = Field(max_length=255, description="Unique client identifier")
    industry: Optional[str] = Field(default=None, max_length=100)
    status: str = Field(default="Active", regex="^(Active|Inactive)$")
    contract_value: Optional[float] = Field(default=None, ge=0)
    
    class Config:
        schema_extra = {
            "example": {
                "client_name": "TechCorp Solutions",
                "industry": "Technology",
                "status": "Active", 
                "contract_value": 50000
            }
        }
```

#### **Response Models**
```python
class AnalyticsResult(BaseModel):
    client_name: str
    metric_type: str
    value: float
    confidence_score: float = Field(ge=0.0, le=1.0)
    explanation: Optional[str] = None
    requires_review: bool = False
    recommendations: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class ProfitabilityResult(AnalyticsResult):
    profit_margin: float
    revenue: float
    costs: float
    profit: float
    
class LicenseEfficiencyResult(AnalyticsResult):
    product_name: str
    utilization_rate: float
    seats_purchased: int
    seats_used: int
    waste_amount: float
    efficiency_level: str

class ResourceUtilizationResult(AnalyticsResult):
    staff_name: str
    utilization_rate: float
    billable_percentage: float
    total_hours: float
    billable_hours: float
    avg_hourly_rate: float

class AnalyticsResponse(BaseModel):
    success: bool
    analysis_id: str
    timestamp: datetime
    results: Dict[str, List[AnalyticsResult]]
    summary: Dict[str, Any]
    requires_review_count: int
```

---

## ⚙️ **Configuration Management**

### **Configuration Hierarchy**

1. **Command Line Arguments** (highest priority)
2. **Environment Variables**
3. **Configuration Files** (.env, config.yaml)
4. **Default Values** (lowest priority)

### **Configuration Classes**

```python
from pydantic_settings import BaseSettings
from typing import List, Optional

class DatabaseConfig(BaseSettings):
    type: str = "sqlite"
    url: str = "sqlite:///./data/moatmetrics.db"
    echo: bool = False
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    
    class Config:
        env_prefix = "DATABASE_"

class APIConfig(BaseSettings):
    host: str = "localhost"
    port: int = 8000
    reload: bool = False
    workers: int = 1
    timeout_keep_alive: int = 5
    
    class Config:
        env_prefix = "API_"

class AnalyticsConfig(BaseSettings):
    confidence_threshold: float = 0.7
    enable_shap: bool = False  # Future ML feature
    max_processing_time: int = 30
    max_memory_usage: int = 1024  # MB
    parallel_processing: bool = False  # Future feature
    
    class Config:
        env_prefix = "ANALYTICS_"

class SecurityConfig(BaseSettings):
    secret_key: str
    access_token_expire_minutes: int = 30
    allowed_hosts: List[str] = []
    cors_origins: List[str] = []
    
    class Config:
        env_prefix = "SECURITY_"

class Config(BaseSettings):
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"
    
    # Nested configurations
    database: DatabaseConfig = DatabaseConfig()
    api: APIConfig = APIConfig()
    analytics: AnalyticsConfig = AnalyticsConfig()
    security: SecurityConfig = SecurityConfig()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
```

### **Environment Variable Mapping**

```bash
# Database Configuration
DATABASE_TYPE=postgresql
DATABASE_URL=postgresql://user:pass@host:port/db
DATABASE_ECHO=false
DATABASE_POOL_SIZE=10

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false
API_WORKERS=1

# Analytics Configuration
ANALYTICS_CONFIDENCE_THRESHOLD=0.7
ANALYTICS_ENABLE_SHAP=false
ANALYTICS_MAX_PROCESSING_TIME=30

# Security Configuration
SECURITY_SECRET_KEY=your-secret-key
SECURITY_ACCESS_TOKEN_EXPIRE_MINUTES=30
SECURITY_ALLOWED_HOSTS=["your-domain.com"]
```

---

## 🗄️ **Database Specifications**

### **Schema Design Principles**
- **Normalization**: Third normal form (3NF) compliance
- **Foreign Keys**: Referential integrity with cascade options
- **Indexes**: Optimized for common query patterns
- **Constraints**: Data integrity at database level
- **Audit Trails**: Created/updated timestamps for all tables

### **Entity Relationship Diagram**

```mermaid
erDiagram
    Client ||--o{ Invoice : "has"
    Client ||--o{ TimeLog : "tracks_time_for"
    Client ||--o{ License : "owns"
    
    Client {
        int id PK
        string client_name UK
        string industry
        string status
        decimal contract_value
        datetime created_at
        datetime updated_at
    }
    
    Invoice {
        int id PK
        string invoice_id UK
        string client_name FK
        decimal amount
        datetime date
        string status
        string description
        datetime created_at
    }
    
    TimeLog {
        int id PK
        string staff_name
        string client_name FK
        decimal hours
        decimal rate
        boolean billable
        datetime date
        string project
        string task_description
        datetime created_at
    }
    
    License {
        int id PK
        string client_name FK
        string product_name
        string vendor
        int seats_purchased
        int seats_used
        decimal cost_per_seat
        string status
        datetime created_at
    }
```

### **Database Indexes**

```sql
-- Performance optimization indexes
CREATE INDEX idx_invoices_client_date ON invoices(client_name, date);
CREATE INDEX idx_invoices_status ON invoices(status);
CREATE INDEX idx_time_logs_client_date ON time_logs(client_name, date);
CREATE INDEX idx_time_logs_staff_date ON time_logs(staff_name, date);
CREATE INDEX idx_time_logs_billable ON time_logs(billable);
CREATE INDEX idx_licenses_client_product ON licenses(client_name, product_name);
CREATE INDEX idx_licenses_status ON licenses(status);

-- Foreign key indexes for performance
CREATE INDEX idx_invoices_client_name ON invoices(client_name);
CREATE INDEX idx_time_logs_client_name ON time_logs(client_name);
CREATE INDEX idx_licenses_client_name ON licenses(client_name);
```

### **Data Constraints**

```sql
-- Business logic constraints
ALTER TABLE time_logs ADD CONSTRAINT check_hours_range 
    CHECK (hours >= 0 AND hours <= 24);

ALTER TABLE time_logs ADD CONSTRAINT check_positive_rate 
    CHECK (rate >= 0);

ALTER TABLE licenses ADD CONSTRAINT check_positive_seats_purchased 
    CHECK (seats_purchased > 0);

ALTER TABLE licenses ADD CONSTRAINT check_seats_used_logical 
    CHECK (seats_used >= 0 AND seats_used <= seats_purchased);

ALTER TABLE licenses ADD CONSTRAINT check_positive_cost 
    CHECK (cost_per_seat >= 0);

ALTER TABLE invoices ADD CONSTRAINT check_positive_amount 
    CHECK (amount >= 0);
```

---

## 🔐 **Security Specifications**

### **Authentication & Authorization**

#### **Role-Based Access Control**
```python
from enum import Enum
from typing import List, Set

class UserRole(Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"

class Permission(Enum):
    READ_DATA = "read_data"
    WRITE_DATA = "write_data"
    RUN_ANALYTICS = "run_analytics"
    MANAGE_USERS = "manage_users"
    APPROVE_REVIEWS = "approve_reviews"
    EXPORT_DATA = "export_data"

ROLE_PERMISSIONS: Dict[UserRole, Set[Permission]] = {
    UserRole.ADMIN: {
        Permission.READ_DATA,
        Permission.WRITE_DATA,
        Permission.RUN_ANALYTICS,
        Permission.MANAGE_USERS,
        Permission.APPROVE_REVIEWS,
        Permission.EXPORT_DATA
    },
    UserRole.ANALYST: {
        Permission.READ_DATA,
        Permission.WRITE_DATA,
        Permission.RUN_ANALYTICS,
        Permission.EXPORT_DATA
    },
    UserRole.VIEWER: {
        Permission.READ_DATA
    }
}
```

#### **Input Validation & Sanitization**
```python
from pydantic import validator, Field
import re

class SecureDataModel(BaseModel):
    client_name: str = Field(max_length=255)
    
    @validator('client_name')
    def sanitize_client_name(cls, v):
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', '', v)
        sanitized = sanitized.strip()
        if not sanitized:
            raise ValueError("Client name cannot be empty")
        return sanitized
    
    amount: float = Field(ge=0, le=999999999.99)
    
    @validator('amount')
    def validate_amount(cls, v):
        if v < 0:
            raise ValueError("Amount cannot be negative")
        return round(v, 2)
```

### **Data Protection**

#### **Sensitive Data Handling**
```python
from cryptography.fernet import Fernet
import os

class DataEncryption:
    """
    Encryption utilities for sensitive data (when needed)
    """
    
    def __init__(self):
        self.key = os.environ.get('ENCRYPTION_KEY') or Fernet.generate_key()
        self.cipher_suite = Fernet(self.key)
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive string data"""
        return self.cipher_suite.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive string data"""
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()
```

---

## 🚀 **Performance Specifications**

### **Response Time Requirements**

| **Operation** | **Target** | **Maximum** | **Notes** |
|---|---|---|---|
| **Health Check** | <50ms | 100ms | No database queries |
| **Simple API Calls** | <200ms | 500ms | Single table queries |
| **File Upload** | <2s/MB | 5s/MB | Includes validation |
| **Analytics Computation** | <30s | 60s | Full dataset analysis |
| **Database Queries** | <100ms | 300ms | Optimized with indexes |

### **Throughput Requirements**

| **Metric** | **Current** | **Target** | **Max** |
|---|---|---|---|
| **Concurrent Users** | 10 | 100 | 500 |
| **API Requests/second** | 50 | 200 | 1000 |
| **File Uploads/hour** | 60 | 240 | 600 |
| **Analytics Runs/hour** | 30 | 120 | 300 |

### **Resource Limits**

```python
# Performance configuration
PERFORMANCE_CONFIG = {
    "max_file_size_mb": 100,
    "max_records_per_file": 100000,
    "max_concurrent_analytics": 5,
    "max_memory_usage_mb": 1024,
    "request_timeout_seconds": 60,
    "analytics_timeout_seconds": 300
}
```

### **Memory Management**

```python
import gc
import psutil
from contextlib import contextmanager

class ResourceManager:
    """
    Memory and resource management utilities
    """
    
    @contextmanager
    def memory_limit(self, limit_mb: int):
        """Context manager for memory-constrained operations"""
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        try:
            yield
        finally:
            current_memory = psutil.Process().memory_info().rss / 1024 / 1024
            if current_memory > initial_memory + limit_mb:
                gc.collect()  # Force garbage collection
    
    def check_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage statistics"""
        process = psutil.Process()
        return {
            "memory_mb": process.memory_info().rss / 1024 / 1024,
            "memory_percent": process.memory_percent(),
            "cpu_percent": process.cpu_percent()
        }
```

---

## 📝 **Logging Specifications**

### **Logging Architecture**

```python
from loguru import logger
import sys
from typing import Dict, Any

# Logging configuration
LOGGING_CONFIG = {
    "handlers": [
        {
            "sink": sys.stdout,
            "level": "INFO",
            "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        },
        {
            "sink": "logs/moatmetrics.log",
            "level": "DEBUG",
            "format": "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            "rotation": "10 MB",
            "retention": "30 days",
            "compression": "gz"
        },
        {
            "sink": "logs/error.log",
            "level": "ERROR",
            "format": "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}\n{exception}",
            "rotation": "10 MB",
            "retention": "90 days"
        }
    ]
}

class StructuredLogger:
    """
    Structured logging for analytics and audit trails
    """
    
    def log_analytics_start(self, analysis_id: str, request_params: Dict[str, Any]):
        logger.info(
            "Analytics started",
            extra={
                "analysis_id": analysis_id,
                "metric_types": request_params.get("metric_types"),
                "client_count": len(request_params.get("client_ids", [])),
                "date_range": {
                    "start": request_params.get("start_date"),
                    "end": request_params.get("end_date")
                }
            }
        )
    
    def log_analytics_complete(self, analysis_id: str, results_summary: Dict[str, Any]):
        logger.info(
            "Analytics completed",
            extra={
                "analysis_id": analysis_id,
                "metrics_computed": results_summary.get("total_metrics"),
                "avg_confidence": results_summary.get("avg_confidence"),
                "review_flagged": results_summary.get("requires_review_count"),
                "processing_time_ms": results_summary.get("processing_time_ms")
            }
        )
    
    def log_data_upload(self, data_type: str, records_processed: int, validation_errors: List[str]):
        logger.info(
            "Data upload completed",
            extra={
                "data_type": data_type,
                "records_processed": records_processed,
                "records_failed": len(validation_errors),
                "validation_errors": validation_errors[:5]  # Limit error list
            }
        )
```

### **Audit Trail Specifications**

```python
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), nullable=True)  # Future: actual user tracking
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(100), nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    timestamp = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Indexes for audit queries
    __table_args__ = (
        Index("idx_audit_logs_timestamp", "timestamp"),
        Index("idx_audit_logs_user_action", "user_id", "action"),
        Index("idx_audit_logs_resource", "resource_type", "resource_id"),
    )

# Audit logging decorator
def audit_action(action: str, resource_type: str):
    """Decorator for automatic audit logging"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                # Log successful action
                _log_audit_action(action, resource_type, "success", 
                                processing_time=time.time() - start_time)
                return result
            except Exception as e:
                # Log failed action
                _log_audit_action(action, resource_type, "failed", error=str(e))
                raise
        return wrapper
    return decorator
```

---

## ⚡ **Error Handling Specifications**

### **Exception Hierarchy**

```python
class MoatMetricsError(Exception):
    """Base exception for all MoatMetrics errors"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

class ValidationError(MoatMetricsError):
    """Data validation errors"""
    pass

class DataIntegrityError(MoatMetricsError):
    """Database integrity constraint violations"""
    pass

class AnalyticsError(MoatMetricsError):
    """Analytics computation errors"""
    pass

class ConfigurationError(MoatMetricsError):
    """Configuration and setup errors"""
    pass

class AuthenticationError(MoatMetricsError):
    """Authentication and authorization errors"""
    pass

class RateLimitError(MoatMetricsError):
    """API rate limiting errors"""
    pass
```

### **Global Error Handler**

```python
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

@app.exception_handler(MoatMetricsError)
async def moatmetrics_exception_handler(request: Request, exc: MoatMetricsError):
    return JSONResponse(
        status_code=400,
        content={
            "success": false,
            "error": exc.__class__.__name__,
            "message": exc.message,
            "details": exc.details,
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": getattr(request.state, "request_id", None)
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "success": false,
            "error": "ValidationError",
            "message": "Request validation failed",
            "details": {
                "validation_errors": exc.errors()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

---

## 🔄 **API Middleware Specifications**

### **Request Processing Pipeline**

```python
from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
import time
import uuid

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all API requests for monitoring and debugging"""
    
    async def dispatch(self, request: Request, call_next):
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Log request start
        start_time = time.time()
        logger.info(
            "Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "client_ip": request.client.host,
                "user_agent": request.headers.get("user-agent")
            }
        )
        
        # Process request
        response = await call_next(request)
        
        # Log request completion
        processing_time = time.time() - start_time
        logger.info(
            "Request completed",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "processing_time_ms": round(processing_time * 1000, 2)
            }
        )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        return response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response
```

### **Rate Limiting**

```python
from collections import defaultdict
from time import time
from typing import Dict, Tuple

class RateLimiter:
    """
    Token bucket rate limiting implementation
    """
    
    def __init__(self):
        self.clients: Dict[str, Tuple[float, int]] = defaultdict(lambda: (time(), 0))
        self.limits = {
            "default": (1000, 3600),  # 1000 requests per hour
            "upload": (100, 3600),    # 100 uploads per hour
            "analytics": (50, 3600)   # 50 analytics runs per hour
        }
    
    def is_allowed(self, client_ip: str, endpoint_type: str = "default") -> bool:
        """Check if request is allowed based on rate limits"""
        now = time()
        max_requests, window = self.limits.get(endpoint_type, self.limits["default"])
        
        last_request_time, request_count = self.clients[client_ip]
        
        # Reset counter if window expired
        if now - last_request_time > window:
            request_count = 0
            last_request_time = now
        
        # Check if under limit
        if request_count < max_requests:
            self.clients[client_ip] = (last_request_time, request_count + 1)
            return True
        
        return False
```

---

## 📊 **Analytics Algorithm Specifications**

### **Profitability Calculation**

```python
def calculate_profitability(
    invoices_df: pd.DataFrame,
    time_logs_df: pd.DataFrame,
    client_name: str
) -> Dict[str, float]:
    """
    Calculate client profitability metrics using statistical methods
    
    Formula:
        Revenue = Sum of invoice amounts (Paid + Pending status)
        Costs = Sum of (hours * hourly_rate) for billable time
        Profit = Revenue - Costs  
        Profit Margin = (Profit / Revenue) * 100 if Revenue > 0 else 0
    
    Args:
        invoices_df: Invoice data for the client
        time_logs_df: Time log data for the client
        client_name: Client identifier
        
    Returns:
        Dictionary with profitability metrics
    """
    
    # Filter data for specific client
    client_invoices = invoices_df[invoices_df['client_name'] == client_name]
    client_time_logs = time_logs_df[time_logs_df['client_name'] == client_name]
    
    # Calculate revenue (exclude cancelled/void invoices)
    revenue_invoices = client_invoices[client_invoices['status'].isin(['Paid', 'Pending'])]
    total_revenue = revenue_invoices['amount'].sum()
    
    # Calculate costs (billable time only)
    billable_time = client_time_logs[client_time_logs['billable'] == True]
    total_costs = (billable_time['hours'] * billable_time['rate']).sum()
    
    # Calculate metrics
    profit = total_revenue - total_costs
    profit_margin = (profit / total_revenue * 100) if total_revenue > 0 else 0
    
    return {
        "revenue": float(total_revenue),
        "costs": float(total_costs),
        "profit": float(profit),
        "profit_margin": float(profit_margin)
    }
```

### **Confidence Scoring Algorithm**

```python
def calculate_confidence_score(
    features_df: pd.DataFrame,
    metric_value: float,
    metric_type: str
) -> Tuple[float, str]:
    """
    Calculate heuristic confidence score (NOT ML-based)
    
    Factors affecting confidence:
    1. Data completeness (missing values)
    2. Data quality (zeros, outliers)  
    3. Consistency (data alignment)
    4. Recency (date ranges)
    
    Args:
        features_df: Input features used in calculation
        metric_value: Calculated metric value
        metric_type: Type of metric being scored
        
    Returns:
        Tuple of (confidence_score, explanation)
    """
    
    base_confidence = 0.8  # Starting confidence
    explanation_parts = []
    
    # Factor 1: Data completeness
    missing_ratio = features_df.isnull().sum().sum() / (len(features_df) * len(features_df.columns))
    completeness_penalty = missing_ratio * 0.3
    base_confidence -= completeness_penalty
    
    if missing_ratio > 0.1:
        explanation_parts.append(f"data completeness: {(1-missing_ratio)*100:.0f}%")
    
    # Factor 2: Zero values (indicate incomplete data)
    zero_penalty = 0
    for col in features_df.select_dtypes(include=[np.number]).columns:
        if (features_df[col] == 0).any():
            zero_penalty += 0.05
    
    base_confidence -= min(zero_penalty, 0.2)  # Cap penalty at 0.2
    
    # Factor 3: Extreme outliers
    for col in features_df.select_dtypes(include=[np.number]).columns:
        Q1 = features_df[col].quantile(0.25)
        Q3 = features_df[col].quantile(0.75)
        IQR = Q3 - Q1
        outliers = features_df[(features_df[col] < (Q1 - 1.5 * IQR)) | 
                              (features_df[col] > (Q3 + 1.5 * IQR))]
        if len(outliers) > 0:
            base_confidence -= 0.1
            explanation_parts.append("potential outliers detected")
    
    # Ensure confidence is in valid range
    confidence_score = max(0.1, min(1.0, base_confidence))
    
    # Generate explanation
    confidence_level = "high" if confidence_score > 0.85 else "medium" if confidence_score > 0.7 else "low"
    explanation = f"Confidence: {confidence_score:.0%} ({confidence_level}"
    
    if explanation_parts:
        explanation += f", {', '.join(explanation_parts)}"
    
    explanation += ")"
    
    return confidence_score, explanation
```

---

## 🔗 **Integration Specifications**

### **External System Interfaces**

#### **PSA Integration (Future)**
```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class PSAConnector(ABC):
    """Abstract base class for PSA system integrations"""
    
    @abstractmethod
    async def get_clients(self) -> List[Dict[str, Any]]:
        """Retrieve client list from PSA system"""
        pass
    
    @abstractmethod
    async def get_invoices(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Retrieve invoices from PSA system"""
        pass
    
    @abstractmethod
    async def get_time_entries(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Retrieve time entries from PSA system"""
        pass

class ConnectWiseConnector(PSAConnector):
    """ConnectWise Manage integration (placeholder for future implementation)"""
    
    def __init__(self, api_url: str, client_id: str, api_key: str):
        self.api_url = api_url
        self.client_id = client_id
        self.api_key = api_key
    
    async def get_clients(self) -> List[Dict[str, Any]]:
        # Future implementation
        pass
```

### **Export Capabilities**

```python
import csv
import json
from io import StringIO
from typing import List, Dict, Any, Union

class ExportService:
    """
    Data export capabilities for analytics results
    """
    
    def export_to_csv(self, results: List[Dict[str, Any]]) -> str:
        """Export analytics results to CSV format"""
        if not results:
            return ""
        
        output = StringIO()
        fieldnames = results[0].keys()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(results)
        
        return output.getvalue()
    
    def export_to_json(self, results: List[Dict[str, Any]]) -> str:
        """Export analytics results to JSON format"""
        return json.dumps(results, indent=2, default=str)
    
    def export_to_excel(self, results: Dict[str, List[Dict[str, Any]]]) -> bytes:
        """Export analytics results to Excel format (future implementation)"""
        # Placeholder for future Excel export capability
        pass
```

---

## 🧪 **Testing Specifications**

### **Test Architecture**

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.api.main import app
from src.db.database import get_db
from src.db.models import Base

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def sample_data(client):
    """Load sample data for testing"""
    # Upload test clients
    with open("tests/fixtures/test_clients.csv", "rb") as f:
        response = client.post("/api/upload/clients", files={"file": f})
    assert response.status_code == 200
    
    # Upload test invoices
    with open("tests/fixtures/test_invoices.csv", "rb") as f:
        response = client.post("/api/upload/invoices", files={"file": f})
    assert response.status_code == 200
    
    return True
```

### **Test Coverage Requirements**

| **Component** | **Minimum Coverage** | **Target Coverage** |
|---|---|---|
| **API Endpoints** | 90% | 95% |
| **Analytics Logic** | 95% | 98% |
| **Data Processing** | 90% | 95% |
| **Error Handling** | 85% | 90% |
| **Configuration** | 80% | 85% |
| **Overall Project** | 85% | 90% |

### **Performance Test Specifications**

```python
import pytest
import time
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient

@pytest.mark.performance
def test_analytics_performance(client, sample_data):
    """Test analytics computation performance"""
    start_time = time.time()
    
    response = client.post("/api/analytics/run", json={
        "metric_types": ["profitability", "license_efficiency", "resource_utilization"]
    })
    
    processing_time = time.time() - start_time
    
    assert response.status_code == 200
    assert processing_time < 30  # Must complete within 30 seconds
    
    results = response.json()
    assert results["success"] == true

@pytest.mark.performance
def test_concurrent_uploads(client):
    """Test concurrent file upload handling"""
    
    def upload_file():
        with open("tests/fixtures/test_clients.csv", "rb") as f:
            response = client.post("/api/upload/clients", files={"file": f})
        return response.status_code
    
    # Test 10 concurrent uploads
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(upload_file) for _ in range(10)]
        results = [future.result() for future in futures]
    
    # All uploads should succeed
    assert all(status == 200 for status in results)
```

---

## 📈 **Monitoring Specifications**

### **Health Check Endpoints**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.db.database import get_db

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check - no dependencies"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@router.get("/health/detailed")
async def detailed_health_check(session: Session = Depends(get_db)):
    """Detailed health check with dependency verification"""
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "services": {}
    }
    
    # Database connectivity
    try:
        session.execute("SELECT 1")
        health_status["services"]["database"] = "connected"
    except Exception as e:
        health_status["services"]["database"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Analytics service
    try:
        from src.services.analytics import AnalyticsService
        analytics = AnalyticsService()
        health_status["services"]["analytics"] = "ready"
    except Exception as e:
        health_status["services"]["analytics"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status
```

### **Metrics Collection**

```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Define metrics
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])
REQUEST_DURATION = Histogram("http_request_duration_seconds", "HTTP request duration")
ANALYTICS_DURATION = Histogram("analytics_duration_seconds", "Analytics computation duration")
ACTIVE_CONNECTIONS = Gauge("database_connections_active", "Active database connections")

class MetricsCollector:
    """
    Prometheus metrics collection
    """
    
    def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics"""
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status_code).inc()
        REQUEST_DURATION.observe(duration)
    
    def record_analytics_duration(self, metric_type: str, duration: float):
        """Record analytics computation time"""
        ANALYTICS_DURATION.labels(metric_type=metric_type).observe(duration)
    
    def update_database_connections(self, count: int):
        """Update active database connection count"""
        ACTIVE_CONNECTIONS.set(count)
```

---

## 🔒 **Security Requirements**

### **Input Validation Specifications**

```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional
import re

class SecureFileUpload(BaseModel):
    """Secure file upload validation"""
    
    filename: str = Field(max_length=255)
    content_type: str
    file_size: int = Field(gt=0, le=100_000_000)  # 100MB max
    
    @validator('filename')
    def validate_filename(cls, v):
        # Allow only safe filename characters
        if not re.match(r'^[a-zA-Z0-9._-]+$', v):
            raise ValueError("Filename contains invalid characters")
        
        # Check file extension
        allowed_extensions = ['.csv', '.xlsx', '.xls']
        if not any(v.lower().endswith(ext) for ext in allowed_extensions):
            raise ValueError("Invalid file type. Only CSV and Excel files allowed")
        
        return v
    
    @validator('content_type')
    def validate_content_type(cls, v):
        allowed_types = ['text/csv', 'application/vnd.ms-excel', 
                        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']
        if v not in allowed_types:
            raise ValueError("Invalid content type")
        return v
```

### **Data Sanitization**

```python
import html
import re
from typing import Any, Union

class DataSanitizer:
    """
    Data sanitization utilities
    """
    
    @staticmethod
    def sanitize_string(value: Union[str, Any]) -> str:
        """Sanitize string input to prevent injection attacks"""
        if not isinstance(value, str):
            value = str(value)
        
        # HTML escape
        value = html.escape(value)
        
        # Remove potentially dangerous patterns
        value = re.sub(r'[<>"\'\n\r\t]', '', value)
        
        # Trim whitespace
        value = value.strip()
        
        return value
    
    @staticmethod
    def sanitize_number(value: Any) -> Union[float, int]:
        """Sanitize numeric input"""
        if isinstance(value, (int, float)):
            return value
        
        if isinstance(value, str):
            # Remove currency symbols and formatting
            cleaned = re.sub(r'[$,\s]', '', value)
            try:
                if '.' in cleaned:
                    return float(cleaned)
                return int(cleaned)
            except ValueError:
                raise ValueError(f"Invalid numeric value: {value}")
        
        raise ValueError(f"Cannot convert {type(value)} to number")
```

---

## 📊 **Data Quality Specifications**

### **Validation Rules**

```python
from typing import List, Dict, Any, Tuple
import pandas as pd

class DataQualityValidator:
    """
    Comprehensive data quality validation
    """
    
    def validate_client_data(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validate client data schema and business rules"""
        errors = []
        
        # Required columns
        required_columns = ['client_name', 'status']
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            errors.append(f"Missing required columns: {missing_columns}")
        
        # Business rules validation
        if 'status' in df.columns:
            invalid_statuses = df[~df['status'].isin(['Active', 'Inactive'])]
            if not invalid_statuses.empty:
                errors.append(f"Invalid status values: {invalid_statuses['status'].unique()}")
        
        if 'contract_value' in df.columns:
            negative_values = df[df['contract_value'] < 0]
            if not negative_values.empty:
                errors.append("Contract values cannot be negative")
        
        # Duplicate checking
        if 'client_name' in df.columns:
            duplicates = df[df.duplicated(subset=['client_name'])]
            if not duplicates.empty:
                errors.append(f"Duplicate client names: {duplicates['client_name'].tolist()}")
        
        return len(errors) == 0, errors
    
    def calculate_quality_score(self, df: pd.DataFrame) -> float:
        """Calculate overall data quality score (0.0-1.0)"""
        total_cells = df.shape[0] * df.shape[1]
        
        # Completeness score
        missing_cells = df.isnull().sum().sum()
        completeness = 1.0 - (missing_cells / total_cells)
        
        # Consistency score (no invalid values)
        consistency = 1.0  # Start with perfect score
        
        # Check for obvious data issues
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            # Penalize extreme outliers
            Q1, Q3 = df[col].quantile([0.25, 0.75])
            IQR = Q3 - Q1
            outliers = df[(df[col] < (Q1 - 3 * IQR)) | (df[col] > (Q3 + 3 * IQR))]
            if not outliers.empty:
                consistency -= 0.1
        
        # Final quality score
        quality_score = (completeness * 0.7) + (max(0, consistency) * 0.3)
        return max(0.0, min(1.0, quality_score))
```

---

## 📁 **File Processing Specifications**

### **File Upload Handler**

```python
from fastapi import UploadFile, HTTPException
import pandas as pd
from typing import Dict, Any
import chardet

class FileProcessor:
    """
    Secure file upload and processing
    """
    
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS = {'.csv', '.xlsx', '.xls'}
    
    async def process_upload(self, file: UploadFile) -> pd.DataFrame:
        """
        Securely process uploaded file
        
        Args:
            file: FastAPI UploadFile object
            
        Returns:
            pandas DataFrame with processed data
            
        Raises:
            HTTPException: File processing errors
        """
        
        # Validate file size
        if file.size > self.MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large")
        
        # Validate file extension
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in self.ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        # Read file content
        content = await file.read()
        
        # Detect encoding
        encoding_result = chardet.detect(content)
        encoding = encoding_result['encoding'] or 'utf-8'
        
        try:
            if file_extension == '.csv':
                # Process CSV file
                df = pd.read_csv(
                    StringIO(content.decode(encoding)),
                    dtype=str,  # Read all as strings initially
                    na_values=['', 'NULL', 'null', 'None', 'N/A']
                )
            elif file_extension in ['.xlsx', '.xls']:
                # Process Excel file
                df = pd.read_excel(
                    BytesIO(content),
                    dtype=str,
                    na_values=['', 'NULL', 'null', 'None', 'N/A']
                )
            
            # Basic sanitization
            df.columns = df.columns.str.strip()  # Remove whitespace from column names
            
            # Remove completely empty rows
            df.dropna(how='all', inplace=True)
            
            return df
            
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"File processing error: {str(e)}")
```

---

## ⚡ **Performance Specifications**

### **Caching Strategy**

```python
from typing import Optional, Any, Dict
import hashlib
import json
from datetime import datetime, timedelta

class ResultsCache:
    """
    In-memory caching for analytics results
    """
    
    def __init__(self, ttl_seconds: int = 3600):  # 1 hour default TTL
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl_seconds = ttl_seconds
    
    def _generate_cache_key(self, request_params: Dict[str, Any]) -> str:
        """Generate cache key from request parameters"""
        # Normalize parameters for consistent caching
        normalized = {
            k: v for k, v in sorted(request_params.items()) 
            if k not in ['include_explanations', 'request_id']
        }
        
        # Create hash of parameters
        params_json = json.dumps(normalized, sort_keys=True, default=str)
        return hashlib.md5(params_json.encode()).hexdigest()
    
    def get(self, request_params: Dict[str, Any]) -> Optional[Any]:
        """Retrieve cached result if valid"""
        cache_key = self._generate_cache_key(request_params)
        
        if cache_key in self.cache:
            cached_item = self.cache[cache_key]
            
            # Check if cache is still valid
            if datetime.utcnow() < cached_item["expires_at"]:
                return cached_item["data"]
            else:
                # Remove expired cache
                del self.cache[cache_key]
        
        return None
    
    def set(self, request_params: Dict[str, Any], result: Any) -> None:
        """Cache result with TTL"""
        cache_key = self._generate_cache_key(request_params)
        
        self.cache[cache_key] = {
            "data": result,
            "cached_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(seconds=self.ttl_seconds)
        }
```

### **Query Optimization**

```python
from sqlalchemy import text
from sqlalchemy.orm import Session

class QueryOptimizer:
    """
    Database query optimization utilities
    """
    
    @staticmethod
    def get_client_profitability_optimized(
        session: Session,
        client_name: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, float]:
        """
        Optimized profitability query using raw SQL for performance
        """
        
        # Build dynamic WHERE clause
        date_filter = ""
        params = {"client_name": client_name}
        
        if start_date and end_date:
            date_filter = "AND i.date BETWEEN :start_date AND :end_date AND tl.date BETWEEN :start_date AND :end_date"
            params.update({"start_date": start_date, "end_date": end_date})
        
        # Optimized query with joins
        query = text(f"""
            WITH revenue AS (
                SELECT 
                    client_name,
                    COALESCE(SUM(amount), 0) as total_revenue
                FROM invoices i
                WHERE client_name = :client_name
                  AND status IN ('Paid', 'Pending')
                  {date_filter}
            ),
            costs AS (
                SELECT 
                    client_name,
                    COALESCE(SUM(hours * rate), 0) as total_costs
                FROM time_logs tl
                WHERE client_name = :client_name
                  AND billable = true
                  {date_filter}
            )
            SELECT 
                r.client_name,
                r.total_revenue,
                COALESCE(c.total_costs, 0) as total_costs,
                r.total_revenue - COALESCE(c.total_costs, 0) as profit,
                CASE 
                    WHEN r.total_revenue > 0 THEN 
                        ((r.total_revenue - COALESCE(c.total_costs, 0)) / r.total_revenue) * 100
                    ELSE 0 
                END as profit_margin
            FROM revenue r
            LEFT JOIN costs c ON r.client_name = c.client_name
        """)
        
        result = session.execute(query, params).fetchone()
        
        if result:
            return {
                "revenue": float(result.total_revenue),
                "costs": float(result.total_costs), 
                "profit": float(result.profit),
                "profit_margin": float(result.profit_margin)
            }
        
        return {"revenue": 0.0, "costs": 0.0, "profit": 0.0, "profit_margin": 0.0}
```

---

## 📞 **Support & Maintenance**

### **Development Support**
- **Code Review**: All changes require peer review
- **Documentation Updates**: Maintain technical specs with code changes
- **Performance Monitoring**: Regular performance review and optimization

### **Production Support**
- **24/7 Monitoring**: Automated health checks and alerting
- **Performance Baselines**: Established benchmarks for key metrics
- **Incident Response**: Defined procedures for system issues

---

**This technical specification provides comprehensive documentation of MoatMetrics' implementation details, interfaces, and requirements for developers and system architects.** 🚀

---

**Document Status**: Production Ready  
**Next Review**: October 1, 2025  
**Maintainer**: Engineering Team
