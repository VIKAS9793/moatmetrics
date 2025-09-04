"""
Pydantic v2 schemas for data validation in MoatMetrics.

This module provides comprehensive data validation schemas using Pydantic v2
with custom validators for handling ambiguous and inconsistent data.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from enum import Enum
import re

from pydantic import (
    BaseModel, Field, EmailStr, ConfigDict, field_validator,
    model_validator, computed_field
)
from pydantic.functional_validators import AfterValidator
from typing_extensions import Annotated


# Custom types with validation
def validate_currency(v: str) -> str:
    """Validate currency code (ISO 4217)."""
    if not re.match(r'^[A-Z]{3}$', v.upper()):
        raise ValueError('Currency must be 3-letter ISO code')
    return v.upper()


def validate_phone(v: str) -> str:
    """Validate and normalize phone number."""
    # Remove all non-numeric characters
    cleaned = re.sub(r'\D', '', v)
    if len(cleaned) < 10 or len(cleaned) > 15:
        raise ValueError('Invalid phone number length')
    return cleaned


CurrencyCode = Annotated[str, AfterValidator(validate_currency)]
PhoneNumber = Annotated[str, AfterValidator(validate_phone)]


class ConfidenceLevel(str, Enum):
    """Confidence level for analytics results."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    AMBIGUOUS = "ambiguous"


class DataQualityFlag(str, Enum):
    """Data quality indicators."""
    COMPLETE = "complete"
    MISSING_FIELDS = "missing_fields"
    INCONSISTENT = "inconsistent"
    DUPLICATE = "duplicate"
    OUTLIER = "outlier"


# Base schemas with common fields
class TimestampedModel(BaseModel):
    """Base model with timestamp fields."""
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


class AuditableModel(TimestampedModel):
    """Base model with audit fields."""
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


# Client schemas
class ClientBase(BaseModel):
    """Base schema for client data."""
    name: str = Field(..., min_length=1, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[PhoneNumber] = None
    is_active: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure name is not empty and properly formatted."""
        v = v.strip()
        if not v:
            raise ValueError('Client name cannot be empty')
        return v


class ClientCreate(ClientBase):
    """Schema for creating a new client."""
    pass


class ClientUpdate(BaseModel):
    """Schema for updating client data."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[PhoneNumber] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class ClientResponse(BaseModel):
    """Schema for client response."""
    model_config = ConfigDict(from_attributes=True)
    
    client_id: int
    name: str = Field(..., min_length=1, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[PhoneNumber] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    data_quality: Optional[DataQualityFlag] = None
    confidence_score: Optional[float] = Field(None, ge=0, le=1)
    
    @field_validator('contact_phone', mode='before')
    @classmethod
    def validate_phone_before(cls, v):
        """Handle phone validation."""
        if v is None or v == '':
            return None
        return v


# Invoice schemas
class InvoiceLineItem(BaseModel):
    """Schema for invoice line items."""
    description: str
    quantity: float = Field(..., gt=0)
    unit_price: float = Field(..., ge=0)
    tax_rate: float = Field(0, ge=0, le=1)
    discount: float = Field(0, ge=0)
    
    @computed_field
    @property
    def subtotal(self) -> float:
        """Calculate line item subtotal."""
        return (self.quantity * self.unit_price) - self.discount
    
    @computed_field
    @property
    def tax_amount(self) -> float:
        """Calculate tax amount."""
        return self.subtotal * self.tax_rate
    
    @computed_field
    @property
    def total(self) -> float:
        """Calculate line item total."""
        return self.subtotal + self.tax_amount


class InvoiceBase(BaseModel):
    """Base schema for invoice data."""
    client_id: int
    invoice_number: str = Field(..., min_length=1, max_length=100)
    date: datetime
    due_date: Optional[datetime] = None
    currency: CurrencyCode = "USD"
    status: str = Field("pending", max_length=50)
    lines: List[InvoiceLineItem]
    
    @field_validator('invoice_number')
    @classmethod
    def validate_invoice_number(cls, v: str) -> str:
        """Ensure invoice number is unique format."""
        v = v.strip().upper()
        if not v:
            raise ValueError('Invoice number cannot be empty')
        return v
    
    @model_validator(mode='after')
    def validate_dates(self) -> 'InvoiceBase':
        """Ensure due date is after invoice date."""
        if self.due_date and self.due_date < self.date:
            raise ValueError('Due date must be after invoice date')
        return self
    
    @computed_field
    @property
    def subtotal(self) -> float:
        """Calculate invoice subtotal."""
        return sum(line.subtotal for line in self.lines)
    
    @computed_field
    @property
    def tax_amount(self) -> float:
        """Calculate total tax."""
        return sum(line.tax_amount for line in self.lines)
    
    @computed_field
    @property
    def total_amount(self) -> float:
        """Calculate invoice total."""
        return self.subtotal + self.tax_amount


class InvoiceCreate(InvoiceBase):
    """Schema for creating a new invoice."""
    pass


class InvoiceResponse(BaseModel):
    """Schema for invoice response."""
    model_config = ConfigDict(from_attributes=True)
    
    invoice_id: int
    client_id: int
    invoice_number: str
    date: datetime
    due_date: Optional[datetime]
    currency: str
    subtotal: float
    tax_amount: float
    total_amount: float
    status: str
    created_at: datetime
    updated_at: datetime
    data_quality: Optional[DataQualityFlag] = None
    confidence_score: Optional[float] = Field(None, ge=0, le=1)


# Time log schemas
class TimeLogBase(BaseModel):
    """Base schema for time log data."""
    client_id: int
    staff_name: str = Field(..., min_length=1, max_length=255)
    staff_email: Optional[EmailStr] = None
    date: datetime
    hours: float = Field(..., gt=0, le=24)
    rate: float = Field(..., ge=0)
    project_name: Optional[str] = Field(None, max_length=255)
    task_description: Optional[str] = None
    billable: bool = True
    
    @field_validator('hours')
    @classmethod
    def validate_hours(cls, v: float) -> float:
        """Validate reasonable hours."""
        if v <= 0 or v > 24:
            raise ValueError('Hours must be between 0 and 24')
        return v
    
    @computed_field
    @property
    def total_cost(self) -> float:
        """Calculate total cost."""
        return self.hours * self.rate


class TimeLogCreate(TimeLogBase):
    """Schema for creating time log."""
    pass


class TimeLogResponse(BaseModel):
    """Schema for time log response."""
    model_config = ConfigDict(from_attributes=True)
    
    log_id: int
    client_id: int
    staff_name: str
    staff_email: Optional[str]
    date: datetime
    hours: float
    rate: float
    total_cost: float
    project_name: Optional[str]
    task_description: Optional[str]
    billable: bool
    created_at: datetime
    data_quality: Optional[DataQualityFlag] = None


# License schemas
class LicenseBase(BaseModel):
    """Base schema for license data."""
    client_id: int
    product: str = Field(..., min_length=1, max_length=255)
    vendor: Optional[str] = Field(None, max_length=255)
    license_type: Optional[str] = Field(None, max_length=50)
    seats_purchased: int = Field(..., gt=0)
    seats_used: int = Field(0, ge=0)
    cost_per_seat: Optional[float] = Field(None, ge=0)
    total_cost: float = Field(..., ge=0)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: bool = True
    auto_renew: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @model_validator(mode='after')
    def validate_seats(self) -> 'LicenseBase':
        """Ensure seats used doesn't exceed seats purchased."""
        if self.seats_used > self.seats_purchased:
            raise ValueError('Seats used cannot exceed seats purchased')
        return self
    
    @model_validator(mode='after')
    def validate_dates(self) -> 'LicenseBase':
        """Ensure end date is after start date."""
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError('End date must be after start date')
        return self
    
    @computed_field
    @property
    def utilization_rate(self) -> float:
        """Calculate license utilization percentage."""
        if self.seats_purchased == 0:
            return 0.0
        return (self.seats_used / self.seats_purchased) * 100
    
    @computed_field
    @property
    def utilization_status(self) -> str:
        """Determine utilization status."""
        rate = self.utilization_rate
        if rate < 30:
            return "underutilized"
        elif rate < 70:
            return "moderate"
        elif rate < 90:
            return "good"
        else:
            return "optimal"


class LicenseCreate(LicenseBase):
    """Schema for creating license."""
    pass


class LicenseResponse(BaseModel):
    """Schema for license response."""
    model_config = ConfigDict(from_attributes=True)
    
    license_id: int
    client_id: int
    product: str
    vendor: Optional[str]
    license_type: Optional[str]
    seats_purchased: int
    seats_used: int
    cost_per_seat: Optional[float]
    total_cost: float
    utilization_rate: float
    utilization_status: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    is_active: bool
    auto_renew: bool
    created_at: datetime
    updated_at: datetime
    data_quality: Optional[DataQualityFlag] = None


# Analytics schemas
class AnalyticsRequest(BaseModel):
    """Schema for analytics computation request."""
    client_ids: Optional[List[int]] = None
    metric_types: Optional[List[str]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    include_explanations: bool = True
    confidence_threshold: float = Field(0.7, ge=0, le=1)


class AnalyticsResultBase(BaseModel):
    """Base schema for analytics results."""
    snapshot_id: str
    client_id: Optional[int] = None
    metric_type: str
    metric_name: str
    value: float
    confidence_score: float = Field(..., ge=0, le=1)
    explanation: Optional[str] = None
    recommendations: Optional[str] = None
    shap_values: Optional[Dict[str, float]] = None
    feature_importance: Optional[Dict[str, float]] = None
    requires_review: bool = False
    
    @computed_field
    @property
    def confidence_level(self) -> ConfidenceLevel:
        """Determine confidence level based on score."""
        if self.confidence_score >= 0.9:
            return ConfidenceLevel.HIGH
        elif self.confidence_score >= 0.7:
            return ConfidenceLevel.MEDIUM
        elif self.confidence_score >= 0.5:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.AMBIGUOUS


class AnalyticsResultCreate(AnalyticsResultBase):
    """Schema for creating analytics result."""
    pass


class AnalyticsResultResponse(BaseModel):
    """Schema for analytics result response."""
    model_config = ConfigDict(from_attributes=True)
    
    result_id: int
    snapshot_id: str
    client_id: Optional[int]
    metric_type: str
    metric_name: str
    value: float
    confidence_score: float
    confidence_level: str
    explanation: Optional[str]
    recommendations: Optional[str]
    requires_review: bool
    reviewed_by: Optional[str]
    reviewed_at: Optional[datetime]
    computed_at: datetime


# Audit log schemas
class AuditLogCreate(BaseModel):
    """Schema for creating audit log entry."""
    actor: str
    actor_role: Optional[str] = None
    action: str
    target: Optional[str] = None
    target_type: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)


class AuditLogResponse(BaseModel):
    """Schema for audit log response."""
    model_config = ConfigDict(from_attributes=True)
    
    entry_id: int
    timestamp: datetime
    actor: str
    actor_role: Optional[str]
    action: str
    target: Optional[str]
    target_type: Optional[str]
    success: bool
    error_message: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    session_id: Optional[str]


# File upload schemas
class FileUploadRequest(BaseModel):
    """Schema for file upload request."""
    file_type: str = Field(..., pattern="^(csv|xlsx|json)$")
    data_type: str = Field(..., pattern="^(clients|invoices|time_logs|licenses)$")
    validate_schema: bool = True
    create_snapshot: bool = True
    dry_run: bool = False


class FileUploadResponse(BaseModel):
    """Schema for file upload response."""
    success: bool
    records_processed: int
    records_failed: int
    validation_errors: List[Dict[str, Any]] = Field(default_factory=list)
    snapshot_id: Optional[str] = None
    data_quality_flags: List[DataQualityFlag] = Field(default_factory=list)
    confidence_score: float = Field(..., ge=0, le=1)


# Report generation schemas  
class ReportRequest(BaseModel):
    """Schema for report generation request."""
    report_type: str = Field(..., pattern="^(profitability|licenses|spend|summary)$")
    format: str = Field("pdf", pattern="^(pdf|csv|json)$")
    client_ids: Optional[List[int]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    include_audit_trail: bool = True
    include_explanations: bool = True


class ReportResponse(BaseModel):
    """Schema for report response."""
    report_id: str
    file_path: str
    format: str
    generated_at: datetime
    generated_by: str
    record_count: int
    file_size_bytes: int
