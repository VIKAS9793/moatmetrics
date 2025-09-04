"""
Database configuration and models for MoatMetrics.

This module provides SQLAlchemy ORM models and database connection utilities
following strict Python standards with type hints and comprehensive documentation.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
import json

from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime, 
    Boolean, ForeignKey, JSON, Text, Index, Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.pool import StaticPool
from loguru import logger

# Create base class for ORM models
Base = declarative_base()


class ConfidenceLevel(str, Enum):
    """Confidence level enumeration for analytics results."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    AMBIGUOUS = "ambiguous"


class MetricType(str, Enum):
    """Types of metrics computed by analytics engine."""
    PROFITABILITY = "profitability"
    LICENSE_EFFICIENCY = "license_efficiency"
    RESOURCE_UTILIZATION = "resource_utilization"
    SPEND_ANALYSIS = "spend_analysis"
    TREND_ANALYSIS = "trend_analysis"


class ActionType(str, Enum):
    """Types of actions for audit logging."""
    DATA_UPLOAD = "data_upload"
    DATA_DELETE = "data_delete"
    ANALYTICS_RUN = "analytics_run"
    REPORT_GENERATE = "report_generate"
    POLICY_CHANGE = "policy_change"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"


class Client(Base):
    """Client entity model."""
    __tablename__ = "clients"
    
    client_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    industry = Column(String(100))
    contact_email = Column(String(255))
    contact_phone = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    metadata_json = Column(JSON, default={})
    
    # Relationships
    invoices = relationship("Invoice", back_populates="client", cascade="all, delete-orphan")
    time_logs = relationship("TimeLog", back_populates="client", cascade="all, delete-orphan")
    licenses = relationship("License", back_populates="client", cascade="all, delete-orphan")
    analytics_results = relationship("AnalyticsResult", back_populates="client", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_client_name', 'name'),
        Index('idx_client_industry', 'industry'),
    )
    
    def __repr__(self) -> str:
        return f"<Client(id={self.client_id}, name='{self.name}')>"


class Invoice(Base):
    """Invoice entity model."""
    __tablename__ = "invoices"
    
    invoice_id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=False)
    invoice_number = Column(String(100), unique=True, nullable=False)
    date = Column(DateTime, nullable=False)
    due_date = Column(DateTime)
    currency = Column(String(3), default="USD")
    subtotal = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    status = Column(String(50), default="pending")
    lines_json = Column(JSON, nullable=False)  # Store invoice line items
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="invoices")
    
    # Indexes
    __table_args__ = (
        Index('idx_invoice_client', 'client_id'),
        Index('idx_invoice_date', 'date'),
        Index('idx_invoice_status', 'status'),
    )
    
    def __repr__(self) -> str:
        return f"<Invoice(id={self.invoice_id}, number='{self.invoice_number}', amount={self.total_amount})>"


class TimeLog(Base):
    """Time tracking log entity model."""
    __tablename__ = "time_logs"
    
    log_id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=False)
    staff_name = Column(String(255), nullable=False)
    staff_email = Column(String(255))
    date = Column(DateTime, nullable=False)
    hours = Column(Float, nullable=False)
    rate = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)
    project_name = Column(String(255))
    task_description = Column(Text)
    billable = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="time_logs")
    
    # Indexes
    __table_args__ = (
        Index('idx_timelog_client', 'client_id'),
        Index('idx_timelog_date', 'date'),
        Index('idx_timelog_staff', 'staff_name'),
    )
    
    def __repr__(self) -> str:
        return f"<TimeLog(id={self.log_id}, staff='{self.staff_name}', hours={self.hours})>"


class License(Base):
    """Software license tracking entity model."""
    __tablename__ = "licenses"
    
    license_id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=False)
    product = Column(String(255), nullable=False)
    vendor = Column(String(255))
    license_type = Column(String(50))  # perpetual, subscription, etc.
    seats_purchased = Column(Integer, nullable=False)
    seats_used = Column(Integer, default=0)
    cost_per_seat = Column(Float)
    total_cost = Column(Float, nullable=False)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    auto_renew = Column(Boolean, default=False)
    metadata_json = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="licenses")
    
    # Indexes
    __table_args__ = (
        Index('idx_license_client', 'client_id'),
        Index('idx_license_product', 'product'),
        Index('idx_license_active', 'is_active'),
    )
    
    @property
    def utilization_rate(self) -> float:
        """Calculate license utilization rate."""
        if self.seats_purchased == 0:
            return 0.0
        return (self.seats_used / self.seats_purchased) * 100
    
    def __repr__(self) -> str:
        return f"<License(id={self.license_id}, product='{self.product}', utilization={self.utilization_rate:.1f}%)>"


class AnalyticsResult(Base):
    """Analytics computation results with explanations."""
    __tablename__ = "analytics_results"
    
    result_id = Column(Integer, primary_key=True, autoincrement=True)
    snapshot_id = Column(String(100), nullable=False)  # Groups related results
    client_id = Column(Integer, ForeignKey("clients.client_id"))
    metric_type = Column(SQLEnum(MetricType), nullable=False)
    metric_name = Column(String(255), nullable=False)
    value = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)
    confidence_level = Column(SQLEnum(ConfidenceLevel), nullable=False)
    explanation = Column(Text)
    shap_values_json = Column(JSON)  # Store SHAP explanation values
    feature_importance_json = Column(JSON)  # Store feature importance
    recommendations = Column(Text)
    requires_review = Column(Boolean, default=False)
    reviewed_by = Column(String(255))
    reviewed_at = Column(DateTime)
    computed_at = Column(DateTime, default=datetime.utcnow)
    metadata_json = Column(JSON, default={})
    
    # Relationships
    client = relationship("Client", back_populates="analytics_results")
    
    # Indexes
    __table_args__ = (
        Index('idx_analytics_snapshot', 'snapshot_id'),
        Index('idx_analytics_client', 'client_id'),
        Index('idx_analytics_metric', 'metric_type'),
        Index('idx_analytics_confidence', 'confidence_level'),
        Index('idx_analytics_review', 'requires_review'),
    )
    
    def __repr__(self) -> str:
        return f"<AnalyticsResult(id={self.result_id}, metric='{self.metric_type.value}', confidence={self.confidence_score:.2f})>"


class AuditLog(Base):
    """Immutable audit log for compliance and governance."""
    __tablename__ = "audit_logs"
    
    entry_id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    actor = Column(String(255), nullable=False)  # User or system performing action
    actor_role = Column(String(50))
    action = Column(SQLEnum(ActionType), nullable=False)
    target = Column(String(255))  # Resource being acted upon
    target_type = Column(String(50))  # Type of resource
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    ip_address = Column(String(45))  # Support IPv6
    user_agent = Column(String(500))
    session_id = Column(String(100))
    details_json = Column(JSON, default={})  # Additional context
    
    # Indexes
    __table_args__ = (
        Index('idx_audit_timestamp', 'timestamp'),
        Index('idx_audit_actor', 'actor'),
        Index('idx_audit_action', 'action'),
        Index('idx_audit_session', 'session_id'),
    )
    
    def __repr__(self) -> str:
        return f"<AuditLog(id={self.entry_id}, actor='{self.actor}', action='{self.action.value}')>"


class DataSnapshot(Base):
    """Track data snapshots for versioning and rollback."""
    __tablename__ = "data_snapshots"
    
    snapshot_id = Column(String(100), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(255))
    snapshot_type = Column(String(50))  # full, incremental, etc.
    file_path = Column(String(500))
    file_size_bytes = Column(Integer)
    record_count = Column(Integer)
    checksum = Column(String(64))  # SHA-256
    description = Column(Text)
    metadata_json = Column(JSON, default={})
    is_archived = Column(Boolean, default=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_snapshot_created', 'created_at'),
        Index('idx_snapshot_type', 'snapshot_type'),
    )
    
    def __repr__(self) -> str:
        return f"<DataSnapshot(id='{self.snapshot_id}', type='{self.snapshot_type}')>"


class DatabaseManager:
    """Manages database connections and sessions."""
    
    def __init__(self, database_url: str = "sqlite:///./data/moatmetrics.db"):
        """
        Initialize database manager.
        
        Args:
            database_url: Database connection URL
        """
        self.database_url = database_url
        self.engine = None
        self.SessionLocal = None
        self._initialize_database()
    
    def _initialize_database(self) -> None:
        """Initialize database engine and create tables."""
        try:
            # Create engine with connection pooling
            if self.database_url.startswith("sqlite"):
                # SQLite specific settings for concurrent access
                self.engine = create_engine(
                    self.database_url,
                    connect_args={"check_same_thread": False},
                    poolclass=StaticPool,
                    echo=False
                )
            else:
                self.engine = create_engine(
                    self.database_url,
                    pool_size=5,
                    max_overflow=10,
                    pool_pre_ping=True,
                    echo=False
                )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=True,  # Enable autoflush for SQLite compatibility
                bind=self.engine,
                expire_on_commit=False  # Prevent lazy loading issues after commit
            )
            
            # Create all tables
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def get_session(self) -> Session:
        """
        Get a new database session.
        
        Returns:
            SQLAlchemy Session object
        """
        if not self.SessionLocal:
            raise RuntimeError("Database not initialized")
        return self.SessionLocal()
    
    def close(self) -> None:
        """Close database connections."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connections closed")


# Global database manager instance
db_manager: Optional[DatabaseManager] = None


def get_db_manager() -> DatabaseManager:
    """
    Get the global database manager instance.
    
    Returns:
        DatabaseManager instance
    """
    global db_manager
    if not db_manager:
        db_manager = DatabaseManager()
    return db_manager


def get_db_session() -> Session:
    """
    Get a database session for dependency injection.
    
    Yields:
        Database session
        
    Note: Automatically commits successful operations.
    Rolls back on exceptions.
    """
    manager = get_db_manager()
    session = manager.get_session()
    try:
        yield session
        # Commit any successful operations
        if session.is_active:
            session.commit()
    except Exception:
        # On exception, rollback any uncommitted changes
        if session.is_active:
            session.rollback()
        raise
    finally:
        # Close the session
        session.close()
