# API Reference

## 📖 **MoatMetrics REST API Documentation**

Complete reference for all MoatMetrics API endpoints with examples, request/response formats, and integration patterns.

**Base URL**: `http://localhost:8000`  
**API Version**: `v1.0.0`  
**Authentication**: Role-based (Admin/Analyst/Viewer)

---

## 🚀 **Quick Start**

### **Interactive Documentation**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### **Authentication**
```bash
# All requests include automatic role-based authentication
# Default: {"username": "admin", "role": "admin"}
```

### **Content Types**
- **JSON**: `application/json`
- **File Upload**: `multipart/form-data`
- **CSV Export**: `text/csv`

---

## 🏥 **Health & Status**

### **GET /health**
Check system health and status.

#### **Request**
```bash
curl -X GET "http://localhost:8000/health"
```

#### **Response**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-04T15:55:30Z",
  "version": "1.0.0-prototype"
}
```

#### **Response Codes**
- `200`: System healthy
- `503`: System unhealthy

---

## 📄 **Data Upload**

### **POST /api/upload/{data_type}**
Upload and process CSV/Excel files.

#### **Parameters**
- **Path**: `data_type` (required) - One of: `clients`, `invoices`, `time_logs`, `licenses`
- **Query**: `validate_schema` (optional, default: true) - Enable schema validation
- **Query**: `create_snapshot` (optional, default: true) - Create data snapshot
- **Query**: `dry_run` (optional, default: false) - Validate only, don't save

#### **Request**
```bash
curl -X POST "http://localhost:8000/api/upload/clients?validate_schema=false" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@clients.csv"
```

#### **Response**
```json
{
  "success": true,
  "records_processed": 10,
  "records_failed": 0,
  "validation_errors": [],
  "data_quality_score": 0.95,
  "confidence_score": 0.9,
  "snapshot_id": "abc123-def456-ghi789",
  "processing_time_ms": 1250
}
```

#### **Response Codes**
- `200`: Upload successful
- `400`: Invalid file format or data type
- `413`: File too large
- `422`: Validation errors

#### **Supported Data Types**

##### **Clients**
```csv
client_id,name,industry,contact_name,contact_email,contact_phone,is_active
1,"Acme Corp","Technology","John Doe","john@acme.com","555-0123",true
```

##### **Invoices**
```csv
invoice_id,client_id,date,total_amount,status,description
1,1,"2025-01-15",5990.76,"paid","Monthly services"
```

##### **Time Logs**
```csv
log_id,client_id,staff_name,date,hours,rate,billable,description
1,1,"Alice Johnson","2025-01-10",8.5,75.00,true,"System maintenance"
```

##### **Licenses**
```csv
license_id,client_id,product,vendor,seats_purchased,seats_used,total_cost,is_active
1,1,"Office 365","Microsoft",50,45,2500.00,true
```

---

## 🧮 **Analytics**

### **POST /api/analytics/run**
Run comprehensive analytics computations.

#### **Request Body**
```json
{
  "client_ids": [1, 2, 3],
  "metric_types": ["profitability", "license_efficiency", "resource_utilization"],
  "start_date": "2025-01-01T00:00:00",
  "end_date": "2025-12-31T23:59:59",
  "include_explanations": true,
  "confidence_threshold": 0.7
}
```

#### **Request**
```bash
curl -X POST "http://localhost:8000/api/analytics/run" \
  -H "Content-Type: application/json" \
  -d '{
    "client_ids": [1, 2, 3],
    "start_date": "2025-01-01T00:00:00",
    "end_date": "2025-12-31T23:59:59",
    "metric_types": ["profitability"],
    "confidence_threshold": 0.7
  }'
```

#### **Response**
```json
{
  "success": true,
  "snapshot_id": "analytics-abc123-def456",
  "metrics": {
    "profitability": {
      "clients": [
        {
          "client_id": 1,
          "client_name": "Acme Corp",
          "revenue": 15000.50,
          "costs": 8500.25,
          "profit": 6500.25,
          "profit_margin": 43.33,
          "confidence_score": 0.85,
          "confidence_level": "medium",
          "requires_review": false
        }
      ],
      "summary": {
        "avg_profit_margin": 41.2,
        "total_revenue": 45000.00,
        "total_costs": 26500.00,
        "total_profit": 18500.00
      }
    }
  },
  "summary": {
    "total_metrics_computed": 17,
    "metrics_requiring_review": 3,
    "average_confidence": 0.78,
    "confidence_distribution": {
      "high": 5,
      "medium": 9,
      "low": 3
    }
  },
  "approval_requests": [
    {
      "request_id": "req-123",
      "metric": "License Utilization - Office 365",
      "confidence": 0.65,
      "requires_approval": true
    }
  ]
}
```

#### **Metric Types**
- **profitability**: Client revenue vs. costs analysis
- **license_efficiency**: Software license utilization
- **resource_utilization**: Staff productivity analysis
- **spend_analysis**: Budget and spending patterns

#### **Response Codes**
- `200`: Analytics completed successfully
- `400`: Invalid request parameters
- `403`: Insufficient permissions
- `500`: Analytics computation failed

### **GET /api/analytics/results**
Retrieve analytics results with filtering.

#### **Query Parameters**
- `snapshot_id` (optional): Filter by analytics run
- `client_id` (optional): Filter by client
- `metric_type` (optional): Filter by metric type
- `requires_review` (optional): Filter by review status
- `skip` (optional, default: 0): Pagination offset
- `limit` (optional, default: 100): Results per page

#### **Request**
```bash
curl -X GET "http://localhost:8000/api/analytics/results?client_id=1&metric_type=profitability&limit=10"
```

#### **Response**
```json
{
  "results": [
    {
      "result_id": 123,
      "snapshot_id": "analytics-abc123",
      "client_id": 1,
      "metric_type": "profitability",
      "metric_name": "Profit Margin - Acme Corp",
      "value": 43.33,
      "confidence_score": 0.85,
      "confidence_level": "medium",
      "explanation": "Profit margin is healthy based on revenue-to-cost ratio...",
      "recommendations": "Consider optimizing labor costs for improved margins",
      "requires_review": false,
      "computed_at": "2025-09-04T15:30:00Z"
    }
  ],
  "total_count": 1,
  "pagination": {
    "skip": 0,
    "limit": 10,
    "has_more": false
  }
}
```

---

## 👥 **Client Management**

### **GET /api/clients**
List all clients with pagination.

#### **Query Parameters**
- `skip` (optional, default: 0): Pagination offset
- `limit` (optional, default: 100, max: 1000): Results per page

#### **Request**
```bash
curl -X GET "http://localhost:8000/api/clients?skip=0&limit=10"
```

#### **Response**
```json
{
  "clients": [
    {
      "client_id": 1,
      "name": "Acme Corp",
      "industry": "Technology",
      "contact_name": "John Doe",
      "contact_email": "john@acme.com",
      "contact_phone": "555-0123",
      "is_active": true,
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:00:00Z"
    }
  ],
  "total_count": 10,
  "pagination": {
    "skip": 0,
    "limit": 10,
    "has_more": false
  }
}
```

### **GET /api/clients/{client_id}**
Get specific client details.

#### **Request**
```bash
curl -X GET "http://localhost:8000/api/clients/1"
```

#### **Response**
```json
{
  "client_id": 1,
  "name": "Acme Corp",
  "industry": "Technology",
  "contact_name": "John Doe",
  "contact_email": "john@acme.com",
  "contact_phone": "555-0123",
  "is_active": true,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z",
  "statistics": {
    "total_invoices": 5,
    "total_revenue": 25000.00,
    "avg_monthly_revenue": 5000.00,
    "last_invoice_date": "2025-08-15"
  }
}
```

#### **Response Codes**
- `200`: Client found
- `404`: Client not found
- `403`: Insufficient permissions

### **POST /api/clients**
Create a new client.

#### **Request Body**
```json
{
  "name": "New Client Corp",
  "industry": "Healthcare",
  "contact_name": "Jane Smith",
  "contact_email": "jane@newclient.com",
  "contact_phone": "555-0456",
  "is_active": true
}
```

#### **Request**
```bash
curl -X POST "http://localhost:8000/api/clients" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Client Corp",
    "industry": "Healthcare",
    "contact_name": "Jane Smith",
    "contact_email": "jane@newclient.com",
    "contact_phone": "555-0456"
  }'
```

#### **Response**
```json
{
  "client_id": 11,
  "name": "New Client Corp",
  "industry": "Healthcare",
  "contact_name": "Jane Smith",
  "contact_email": "jane@newclient.com",
  "contact_phone": "555-0456",
  "is_active": true,
  "created_at": "2025-09-04T15:55:30Z",
  "updated_at": "2025-09-04T15:55:30Z"
}
```

---

## 📊 **Reports**

### **POST /api/reports/generate**
Generate custom reports.

#### **Request Body**
```json
{
  "report_type": "profitability",
  "format": "pdf",
  "client_ids": [1, 2, 3],
  "start_date": "2025-01-01",
  "end_date": "2025-12-31",
  "include_audit_trail": false,
  "include_explanations": true
}
```

#### **Request**
```bash
curl -X POST "http://localhost:8000/api/reports/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "report_type": "profitability",
    "format": "pdf",
    "client_ids": [1, 2, 3]
  }'
```

#### **Response**
```json
{
  "report_id": "report-abc123-def456",
  "file_path": "/reports/profitability-2025-09-04.pdf",
  "format": "pdf",
  "generated_at": "2025-09-04T15:55:30Z",
  "generated_by": "admin",
  "record_count": 25,
  "file_size_bytes": 1048576,
  "download_url": "/api/reports/report-abc123-def456/download"
}
```

#### **Report Types**
- **profitability**: Client profitability analysis
- **license_efficiency**: License utilization report
- **resource_utilization**: Staff productivity report
- **audit_trail**: Compliance and audit report

#### **Report Formats**
- **pdf**: Formatted PDF report
- **csv**: Raw data export
- **json**: Structured data format

### **GET /api/reports/{report_id}/download**
Download generated report.

#### **Request**
```bash
curl -X GET "http://localhost:8000/api/reports/report-abc123-def456/download" \
  --output report.pdf
```

#### **Response**
Binary file download with appropriate `Content-Type` header.

---

## 🔐 **Governance**

### **GET /api/governance/permissions**
Check user permissions.

#### **Query Parameters**
- `permission` (required): Permission to check
- `resource` (optional): Specific resource

#### **Request**
```bash
curl -X GET "http://localhost:8000/api/governance/permissions?permission=data_read&resource=clients"
```

#### **Response**
```json
{
  "permission": "data_read",
  "resource": "clients",
  "allowed": true,
  "reason": "User has admin role with full access",
  "user_role": "admin"
}
```

### **GET /api/governance/approvals/pending**
Get pending approval requests.

#### **Request**
```bash
curl -X GET "http://localhost:8000/api/governance/approvals/pending"
```

#### **Response**
```json
{
  "pending_requests": [
    {
      "request_id": "req-123",
      "request_type": "analytics_confidence",
      "requester": "system",
      "action": "analytics_result",
      "target": "License Utilization - Office 365",
      "confidence_score": 0.65,
      "created_at": "2025-09-04T15:30:00Z",
      "expires_at": "2025-09-11T15:30:00Z",
      "details": {
        "metric_type": "license_efficiency",
        "client_id": 1,
        "value": 72.5
      }
    }
  ]
}
```

### **POST /api/governance/approvals/{request_id}/process**
Process an approval request.

#### **Request Body**
```json
{
  "approved": true,
  "reason": "Data quality is acceptable for business decision"
}
```

#### **Request**
```bash
curl -X POST "http://localhost:8000/api/governance/approvals/req-123/process" \
  -H "Content-Type: application/json" \
  -d '{
    "approved": true,
    "reason": "Data quality is acceptable"
  }'
```

#### **Response**
```json
{
  "success": true,
  "message": "Approval request processed successfully",
  "request_id": "req-123",
  "approved": true,
  "processed_by": "admin",
  "processed_at": "2025-09-04T15:55:30Z"
}
```

### **GET /api/governance/compliance/{framework}**
Check compliance with specific framework.

#### **Request**
```bash
curl -X GET "http://localhost:8000/api/governance/compliance/gdpr"
```

#### **Response**
```json
{
  "framework": "gdpr",
  "compliant": true,
  "last_assessed": "2025-09-04T15:55:30Z",
  "requirements": {
    "data_minimization": "compliant",
    "consent_management": "compliant",
    "right_to_deletion": "compliant",
    "data_portability": "compliant",
    "audit_trail": "compliant"
  },
  "recommendations": []
}
```

---

## 📝 **Audit Logs**

### **GET /api/audit/logs**
Retrieve audit logs with filtering.

#### **Query Parameters**
- `actor` (optional): Filter by user
- `action` (optional): Filter by action type
- `start_date` (optional): Filter by date range
- `end_date` (optional): Filter by date range
- `limit` (optional, default: 100): Results per page

#### **Request**
```bash
curl -X GET "http://localhost:8000/api/audit/logs?actor=admin&action=data_upload&limit=50"
```

#### **Response**
```json
{
  "logs": [
    {
      "entry_id": 1001,
      "timestamp": "2025-09-04T15:55:30Z",
      "actor": "admin",
      "actor_role": "admin",
      "action": "data_upload",
      "target": "clients.csv",
      "target_type": "file",
      "success": true,
      "ip_address": "127.0.0.1",
      "user_agent": "curl/7.64.1",
      "details": {
        "records_processed": 10,
        "file_size": 2048,
        "processing_time_ms": 1250
      }
    }
  ],
  "total_count": 150,
  "pagination": {
    "limit": 50,
    "has_more": true
  }
}
```

---

## 🔌 **Integration Patterns**

### **Batch Data Processing**
```python
import requests

# Upload multiple files in sequence
files = [
    ('clients.csv', 'clients'),
    ('invoices.csv', 'invoices'),
    ('time_logs.csv', 'time_logs'),
    ('licenses.csv', 'licenses')
]

for filename, data_type in files:
    with open(filename, 'rb') as f:
        response = requests.post(
            f'http://localhost:8000/api/upload/{data_type}',
            files={'file': f},
            params={'validate_schema': False}
        )
    print(f"{filename}: {response.json()['records_processed']} records")
```

### **Automated Analytics Pipeline**
```python
import requests
import time

# 1. Upload data
upload_response = requests.post(
    'http://localhost:8000/api/upload/clients',
    files={'file': open('clients.csv', 'rb')}
)

# 2. Run analytics
analytics_response = requests.post(
    'http://localhost:8000/api/analytics/run',
    json={
        'client_ids': [1, 2, 3],
        'metric_types': ['profitability'],
        'start_date': '2025-01-01T00:00:00',
        'end_date': '2025-12-31T23:59:59'
    }
)

snapshot_id = analytics_response.json()['snapshot_id']

# 3. Generate report
report_response = requests.post(
    'http://localhost:8000/api/reports/generate',
    json={
        'report_type': 'profitability',
        'format': 'pdf',
        'client_ids': [1, 2, 3]
    }
)

report_id = report_response.json()['report_id']

# 4. Download report
report_file = requests.get(
    f'http://localhost:8000/api/reports/{report_id}/download'
)

with open('profitability_report.pdf', 'wb') as f:
    f.write(report_file.content)
```

### **Real-time Monitoring**
```python
import requests
import schedule
import time

def check_system_health():
    response = requests.get('http://localhost:8000/health')
    if response.status_code != 200:
        print("🚨 System unhealthy!")
        # Send alert
    else:
        print("✅ System healthy")

# Check every 5 minutes
schedule.every(5).minutes.do(check_system_health)

while True:
    schedule.run_pending()
    time.sleep(60)
```

---

## ❌ **Error Handling**

### **Common Error Responses**

#### **Validation Error (422)**
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "client_ids"],
      "msg": "Field required",
      "input": null
    }
  ]
}
```

#### **Permission Denied (403)**
```json
{
  "detail": "Insufficient permissions for this operation"
}
```

#### **Not Found (404)**
```json
{
  "detail": "Client not found"
}
```

#### **Internal Server Error (500)**
```json
{
  "detail": "Analytics computation failed",
  "error_id": "err-abc123",
  "timestamp": "2025-09-04T15:55:30Z"
}
```

### **Error Handling Best Practices**
```python
import requests

def safe_api_call(url, **kwargs):
    try:
        response = requests.request(**kwargs)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 422:
            print("Validation error:", e.response.json())
        elif e.response.status_code == 403:
            print("Permission denied")
        elif e.response.status_code == 500:
            print("Server error")
        return None
    except requests.exceptions.RequestException as e:
        print("Network error:", str(e))
        return None
```

---

## 📊 **Rate Limits & Performance**

### **Rate Limits**
- **Standard endpoints**: 100 requests/minute
- **Upload endpoints**: 10 requests/minute
- **Analytics endpoints**: 5 requests/minute

### **Performance Tips**
1. **Batch Operations**: Upload multiple files in sequence
2. **Pagination**: Use appropriate page sizes (100-1000)
3. **Caching**: Cache frequently accessed data
4. **Async Processing**: Use background tasks for large operations

### **Response Time SLAs**
- **Health check**: <50ms
- **Data retrieval**: <200ms
- **File upload**: <2s per MB
- **Analytics computation**: <30s
- **Report generation**: <60s

---

## 🔗 **SDK & Libraries**

### **Python SDK** (Coming Soon)
```python
from moatmetrics import MoatMetricsClient

client = MoatMetricsClient(base_url="http://localhost:8000")

# Upload data
result = client.upload_file("clients.csv", data_type="clients")

# Run analytics
analytics = client.run_analytics(
    client_ids=[1, 2, 3],
    metrics=["profitability"]
)

# Generate report
report = client.generate_report(
    report_type="profitability",
    format="pdf"
)
```

### **JavaScript SDK** (Planned)
```javascript
import { MoatMetricsAPI } from 'moatmetrics-js';

const api = new MoatMetricsAPI('http://localhost:8000');

// Upload and analyze
const result = await api.uploadAndAnalyze({
  file: clientsFile,
  dataType: 'clients',
  runAnalytics: true
});
```

---

## 📞 **Support**

### **API Support**
- 📧 **API Issues**: api-support@moatmetrics.com
- 📚 **Documentation**: http://localhost:8000/docs
- 🐛 **Bug Reports**: GitHub Issues
- 💬 **Community**: Discord #api-help

### **SLA Commitments**
- **Uptime**: 99.9% availability
- **Response Time**: <200ms for standard endpoints
- **Support Response**: <24 hours for API issues

---

**Last Updated**: September 4, 2025  
**API Version**: 1.0.0  
**Documentation Version**: 1.0
