# Integration Guide

## 📋 **Document Overview**

**Document Type**: Integration Guide  
**Version**: 1.0.0  
**Owner**: Engineering Team  
**Last Updated**: September 4, 2025  
**Review Cycle**: Monthly  
**Status**: Active

**Audience**: System Administrators, Integration Engineers, MSP Technical Staff

---

## 🎯 **Overview**

MoatMetrics is designed to integrate seamlessly with existing MSP toolchains through secure APIs, file-based imports, and webhook integrations. This guide covers all supported integration methods and provides step-by-step instructions for connecting your PSA, RMM, and cloud service provider systems.

### **Core Integration Philosophy**
- **Privacy-First**: All data processing occurs locally
- **API-Driven**: RESTful APIs with OpenAPI 3.0 specifications
- **Event-Based**: Real-time updates via webhooks when available
- **Fallback Support**: File-based imports for systems without APIs

---

## 🔧 **Supported Systems**

### **Professional Services Automation (PSA)**

| **System** | **Integration Type** | **Support Level** | **Setup Time** |
|---|---|---|---|
| **ConnectWise Manage** | API + Webhooks | ✅ Full Support | 15 minutes |
| **Autotask PSA** | API + Webhooks | ✅ Full Support | 15 minutes |
| **ServiceNow ITSM** | API + Webhooks | ✅ Full Support | 20 minutes |
| **FreshService** | API + Webhooks | ✅ Full Support | 10 minutes |
| **Zendesk** | API + Webhooks | 🔶 Partial Support | 15 minutes |
| **Salesforce Service Cloud** | API + Webhooks | ✅ Full Support | 25 minutes |
| **Custom PSA** | CSV Import | 🔶 Manual Process | 30 minutes |

### **Remote Monitoring & Management (RMM)**

| **System** | **Integration Type** | **Support Level** | **Setup Time** |
|---|---|---|---|
| **Datto RMM** | API + Webhooks | ✅ Full Support | 15 minutes |
| **N-able N-central** | API + Webhooks | ✅ Full Support | 20 minutes |
| **ConnectWise Automate** | API + Webhooks | ✅ Full Support | 15 minutes |
| **Kaseya VSA** | API + Webhooks | ✅ Full Support | 20 minutes |
| **Atera** | API + Webhooks | ✅ Full Support | 10 minutes |
| **NinjaOne** | API + Webhooks | ✅ Full Support | 15 minutes |
| **PRTG** | API | 🔶 Monitoring Only | 20 minutes |

### **Cloud Service Providers**

| **Provider** | **Integration Type** | **Support Level** | **Setup Time** |
|---|---|---|---|
| **Microsoft 365/Azure** | Graph API + Billing API | ✅ Full Support | 20 minutes |
| **Google Workspace/GCP** | Admin SDK + Billing API | ✅ Full Support | 25 minutes |
| **AWS** | Organizations API + Billing | ✅ Full Support | 30 minutes |
| **Generic Cloud** | CSV Import | 🔶 Manual Process | 15 minutes |

### **Additional Systems**

| **Type** | **System** | **Integration** | **Support Level** |
|---|---|---|---|
| **Backup** | Datto SIRIS, Veeam | API | ✅ Full Support |
| **Security** | CrowdStrike, SentinelOne | API | 🔶 Partial Support |
| **Networking** | Meraki, Ubiquiti | API | 🔶 Monitoring Only |
| **Finance** | QuickBooks, Xero | API | ✅ Full Support |

---

## 🚀 **Quick Start Integration**

### **Step 1: Prerequisites**

#### **System Requirements**
- MoatMetrics installed and running
- Admin access to systems being integrated
- Network connectivity between systems
- API credentials for target systems

#### **Preparation Checklist**
- [ ] Document current system versions
- [ ] Gather API credentials and endpoints
- [ ] Identify data sync frequency requirements
- [ ] Plan integration testing approach
- [ ] Prepare rollback procedures

### **Step 2: Integration Setup Wizard**

Access the MoatMetrics Integration Setup:

```bash path=null start=null
# Launch MoatMetrics Integration Wizard
python -m moatmetrics.cli integration setup

# Or via web interface
# Navigate to Settings → Integrations → Add New
```

### **Step 3: Test Integration**

```bash path=null start=null
# Test all configured integrations
python -m moatmetrics.cli integration test-all

# Test specific integration
python -m moatmetrics.cli integration test --system=connectwise
```

---

## 🔗 **API Integration Details**

### **Authentication Methods**

#### **1. API Key Authentication**
```python path=null start=null
# Standard API key configuration
headers = {
    'Authorization': 'Bearer {api_key}',
    'Content-Type': 'application/json'
}
```

#### **2. OAuth 2.0 Flow**
```python path=null start=null
# OAuth 2.0 configuration for Microsoft Graph
oauth_config = {
    'client_id': 'your_client_id',
    'client_secret': 'your_client_secret',
    'tenant_id': 'your_tenant_id',
    'scope': 'https://graph.microsoft.com/.default'
}
```

#### **3. Certificate-Based Authentication**
```bash path=null start=null
# Certificate setup for enhanced security
openssl req -newkey rsa:2048 -nodes -keyout moatmetrics.key \
    -x509 -days 365 -out moatmetrics.crt
```

### **Rate Limiting & Retry Logic**

All integrations implement intelligent rate limiting:

```python path=null start=null
# Built-in rate limiting configuration
rate_limits = {
    'requests_per_second': 10,
    'requests_per_minute': 600,
    'retry_attempts': 3,
    'backoff_strategy': 'exponential'
}
```

---

## 🏗️ **PSA System Integration**

### **ConnectWise Manage**

#### **Prerequisites**
- ConnectWise Manage v2022.1 or later
- API member with appropriate permissions
- Company database access

#### **Setup Process**

```bash path=null start=null
# ConnectWise API configuration
export CW_API_URL="https://api-na.myconnectwise.net/v4_6_release/apis/3.0"
export CW_COMPANY_ID="YourCompanyID"
export CW_PUBLIC_KEY="your_public_key"
export CW_PRIVATE_KEY="your_private_key"
export CW_CLIENT_ID="your_client_id"
```

#### **Integration Configuration**

```json
{
  "integration": {
    "name": "ConnectWise Manage",
    "type": "psa",
    "api_version": "3.0",
    "sync_frequency": "hourly",
    "endpoints": {
      "companies": "/company/companies",
      "contacts": "/company/contacts",
      "agreements": "/finance/agreements",
      "time_entries": "/time/entries",
      "expenses": "/expense/entries",
      "invoices": "/finance/invoices",
      "products": "/procurement/products",
      "tickets": "/service/tickets"
    },
    "data_mapping": {
      "client_id": "company.id",
      "client_name": "company.identifier",
      "contract_value": "agreement.amount",
      "billing_method": "agreement.billingCycle"
    }
  }
}
```

#### **Data Sync Process**

```python path=null start=null
# ConnectWise data synchronization
from moatmetrics.integrations.psa import ConnectWiseIntegration

cw = ConnectWiseIntegration(
    api_url=os.getenv('CW_API_URL'),
    company_id=os.getenv('CW_COMPANY_ID'),
    public_key=os.getenv('CW_PUBLIC_KEY'),
    private_key=os.getenv('CW_PRIVATE_KEY'),
    client_id=os.getenv('CW_CLIENT_ID')
)

# Sync all PSA data
cw.sync_companies()
cw.sync_agreements()
cw.sync_time_entries()
cw.sync_expenses()
cw.sync_invoices()
```

### **Autotask PSA**

#### **Setup Process**

```bash path=null start=null
# Autotask API configuration
export AT_API_URL="https://webservices2.autotask.net/atservices/1.6/atws.asmx"
export AT_USERNAME="your_username"
export AT_PASSWORD="your_password"
export AT_TRACKING_ID="your_tracking_id"
```

#### **Integration Configuration**

```json
{
  "integration": {
    "name": "Autotask PSA",
    "type": "psa",
    "api_version": "1.6",
    "sync_frequency": "hourly",
    "endpoints": {
      "accounts": "Account",
      "contracts": "Contract",
      "time_entries": "TimeEntry",
      "tickets": "Ticket",
      "products": "Product",
      "invoices": "Invoice"
    }
  }
}
```

---

## 💻 **RMM System Integration**

### **Datto RMM**

#### **Prerequisites**
- Datto RMM platform access
- API credentials with read permissions
- Site filtering configuration

#### **Setup Process**

```bash path=null start=null
# Datto RMM API configuration
export DATTO_API_URL="https://your_region.centrastage.net/api"
export DATTO_API_KEY="your_api_key"
export DATTO_SECRET_KEY="your_secret_key"
```

#### **Device and Monitoring Data Sync**

```json
{
  "integration": {
    "name": "Datto RMM",
    "type": "rmm",
    "sync_frequency": "every_15_minutes",
    "endpoints": {
      "sites": "/sites",
      "devices": "/devices",
      "alerts": "/alerts",
      "software": "/software",
      "patches": "/patches",
      "antivirus": "/antivirus"
    },
    "metrics": [
      "device_count",
      "uptime_percentage",
      "alert_volume",
      "patch_compliance",
      "antivirus_status"
    ]
  }
}
```

### **N-able N-central**

#### **Setup Process**

```bash path=null start=null
# N-able N-central configuration
export NABLE_SERVER_URL="https://your_server.n-able.com"
export NABLE_USERNAME="your_username"
export NABLE_PASSWORD="your_password"
export NABLE_JWT_TOKEN="your_jwt_token"
```

#### **Data Extraction**

```python path=null start=null
# N-able data sync
from moatmetrics.integrations.rmm import NAbleIntegration

nable = NAbleIntegration(
    server_url=os.getenv('NABLE_SERVER_URL'),
    username=os.getenv('NABLE_USERNAME'),
    password=os.getenv('NABLE_PASSWORD')
)

# Sync monitoring data
nable.sync_devices()
nable.sync_services()
nable.sync_performance_data()
```

---

## ☁️ **Cloud Provider Integration**

### **Microsoft 365 & Azure**

#### **Prerequisites**
- Azure AD app registration
- Microsoft Graph API permissions
- Partner Center access (for CSP)

#### **App Registration Setup**

```bash path=null start=null
# Azure CLI setup for app registration
az login
az ad app create --display-name "MoatMetrics Integration" \
    --required-resource-accesses @manifest.json

# Grant admin consent
az ad app permission admin-consent --id {app-id}
```

#### **Required Permissions**

```json
{
  "requiredResourceAccess": [
    {
      "resourceAppId": "00000003-0000-0000-c000-000000000000",
      "resourceAccess": [
        {
          "id": "bf394140-e372-4bf9-a898-299cfc7564e5",
          "type": "Role"
        },
        {
          "id": "230c1aed-a721-4c5d-9cb4-a90514e508ef",
          "type": "Role"
        }
      ]
    }
  ]
}
```

#### **Data Synchronization**

```python path=null start=null
# Microsoft Graph integration
from moatmetrics.integrations.cloud import MicrosoftGraphIntegration

graph = MicrosoftGraphIntegration(
    tenant_id=os.getenv('AZURE_TENANT_ID'),
    client_id=os.getenv('AZURE_CLIENT_ID'),
    client_secret=os.getenv('AZURE_CLIENT_SECRET')
)

# Sync license and usage data
graph.sync_subscriptions()
graph.sync_license_usage()
graph.sync_billing_data()
```

### **Google Workspace & GCP**

#### **Service Account Setup**

```bash path=null start=null
# Create service account for Google integration
gcloud iam service-accounts create moatmetrics-integration \
    --display-name="MoatMetrics Integration Account"

# Download service account key
gcloud iam service-accounts keys create moatmetrics-key.json \
    --iam-account=moatmetrics-integration@project-id.iam.gserviceaccount.com
```

#### **Required Scopes**

```python path=null start=null
# Google API scopes required
GOOGLE_SCOPES = [
    'https://www.googleapis.com/auth/admin.directory.user.readonly',
    'https://www.googleapis.com/auth/admin.directory.group.readonly',
    'https://www.googleapis.com/auth/admin.directory.domain.readonly',
    'https://www.googleapis.com/auth/cloud-billing.readonly',
    'https://www.googleapis.com/auth/cloud-platform.read-only'
]
```

### **AWS Integration**

#### **IAM Setup**

```bash path=null start=null
# Create IAM user for MoatMetrics
aws iam create-user --user-name moatmetrics-integration

# Attach required policies
aws iam attach-user-policy --user-name moatmetrics-integration \
    --policy-arn arn:aws:iam::aws:policy/AWSBillingReadOnlyAccess

aws iam attach-user-policy --user-name moatmetrics-integration \
    --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess

# Create access keys
aws iam create-access-key --user-name moatmetrics-integration
```

#### **Data Collection**

```python path=null start=null
# AWS billing and usage integration
from moatmetrics.integrations.cloud import AWSIntegration

aws = AWSIntegration(
    access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region=os.getenv('AWS_DEFAULT_REGION')
)

# Sync billing and resource data
aws.sync_billing_data()
aws.sync_ec2_instances()
aws.sync_s3_usage()
```

---

## 🔄 **Integration Patterns**

### **Pattern 1: Real-Time Webhooks**

#### **Webhook Registration**

```python path=null start=null
# Register webhook endpoint with PSA system
webhook_config = {
    'endpoint': 'https://your-moatmetrics.local/api/webhooks/psa',
    'events': ['ticket.created', 'ticket.closed', 'time_entry.added'],
    'secret': 'webhook_secret_key',
    'timeout': 30
}

psa_client.register_webhook(webhook_config)
```

#### **Webhook Handler**

```python path=null start=null
# MoatMetrics webhook receiver
@app.route('/api/webhooks/psa', methods=['POST'])
def handle_psa_webhook():
    signature = request.headers.get('X-Webhook-Signature')
    if not verify_webhook_signature(request.data, signature):
        abort(401)
    
    event_data = request.json
    process_psa_event(event_data)
    return jsonify({'status': 'processed'})
```

### **Pattern 2: Scheduled Sync**

#### **Sync Configuration**

```yaml
# Integration sync schedule
sync_schedules:
  psa_data:
    frequency: "hourly"
    offset: "5 minutes"
    retry_count: 3
    
  rmm_monitoring:
    frequency: "15 minutes"
    offset: "0 minutes"
    retry_count: 2
    
  cloud_billing:
    frequency: "daily"
    offset: "2 AM"
    retry_count: 5
```

#### **Sync Implementation**

```python path=null start=null
# Scheduled data synchronization
from moatmetrics.integrations.scheduler import IntegrationScheduler

scheduler = IntegrationScheduler()

@scheduler.task("hourly")
def sync_psa_data():
    """Sync PSA data every hour"""
    integrations = get_active_psa_integrations()
    for integration in integrations:
        try:
            integration.sync_incremental()
            log_sync_success(integration.name)
        except Exception as e:
            log_sync_error(integration.name, e)
            notify_admin(integration.name, e)
```

### **Pattern 3: File-Based Import**

#### **Supported File Formats**
- **CSV**: Standard comma-separated values
- **JSON**: JavaScript Object Notation
- **XML**: Extensible Markup Language
- **Excel**: .xlsx files (via pandas)

#### **Import Process**

```python path=null start=null
# File-based data import
from moatmetrics.integrations.file_import import FileImporter

importer = FileImporter()

# Import client data from CSV
client_mapping = {
    'company_name': 'Client Name',
    'monthly_fee': 'Monthly Recurring Revenue',
    'contract_start': 'Agreement Start Date',
    'services': 'Service Categories'
}

importer.import_csv(
    file_path='client_data.csv',
    data_type='clients',
    field_mapping=client_mapping
)
```

---

## ⚙️ **Data Mapping & Transformation**

### **Standard Data Models**

#### **Client Entity**
```python path=null start=null
# Standard client data model
@dataclass
class Client:
    client_id: str
    name: str
    industry: Optional[str]
    contract_type: str  # managed, break_fix, hybrid
    monthly_fee: Decimal
    contract_start: datetime
    contract_end: Optional[datetime]
    services: List[str]
    contact_info: ContactInfo
    billing_frequency: str  # monthly, quarterly, annual
```

#### **Service Entity**
```python path=null start=null
# Standard service data model
@dataclass
class Service:
    service_id: str
    client_id: str
    service_type: str  # support, monitoring, backup, etc.
    cost_per_hour: Optional[Decimal]
    monthly_fee: Optional[Decimal]
    resource_allocation: Dict[str, float]
    performance_metrics: Dict[str, Any]
```

### **Field Mapping Configuration**

#### **ConnectWise Mapping**
```yaml
# ConnectWise field mappings
connectwise_mapping:
  client:
    moat_field: connectwise_field
    client_id: "company.id"
    name: "company.identifier"
    industry: "company.market"
    monthly_fee: "agreement.amount"
    contract_start: "agreement.startDate"
    contact_email: "company.defaultContact.communicationItems[0].value"
    
  service:
    service_id: "agreementAddition.id"
    service_type: "agreementAddition.product.subcategory.name"
    monthly_fee: "agreementAddition.amount"
```

#### **Custom Mapping**
```python path=null start=null
# Custom field mapping for unique systems
custom_mapping = {
    'transform_functions': {
        'monthly_fee': lambda x: Decimal(str(x).replace('$', '').replace(',', '')),
        'contract_start': lambda x: datetime.strptime(x, '%m/%d/%Y'),
        'services': lambda x: [s.strip() for s in x.split(',')]
    },
    'validation_rules': {
        'monthly_fee': {'min': 0, 'max': 1000000},
        'contract_start': {'format': 'date'},
        'client_name': {'required': True, 'max_length': 255}
    }
}
```

---

## 📊 **Monitoring & Troubleshooting**

### **Integration Health Dashboard**

Access real-time integration status:

```bash path=null start=null
# View integration status
python -m moatmetrics.cli integration status

# Detailed health check
python -m moatmetrics.cli integration health --verbose
```

#### **Health Metrics Tracked**
- **API Response Times**: Average and 95th percentile
- **Success Rates**: Percentage of successful API calls
- **Error Rates**: Categorized by error type
- **Data Freshness**: Time since last successful sync
- **Rate Limit Usage**: Percentage of rate limits consumed

### **Common Integration Issues**

#### **1. Authentication Failures**

```bash path=null start=null
# Debug authentication issues
python -m moatmetrics.cli integration debug-auth --system=connectwise

# Test API connectivity
curl -H "Authorization: Bearer {api_key}" \
     -H "Content-Type: application/json" \
     "{api_endpoint}/test"
```

**Common Causes:**
- Expired API credentials
- Incorrect permission scopes
- IP whitelist restrictions
- Rate limit exceeded

**Solutions:**
- Refresh API tokens
- Verify permission grants
- Add MoatMetrics IP to allowlist
- Implement exponential backoff

#### **2. Data Sync Delays**

```bash path=null start=null
# Check sync queue status
python -m moatmetrics.cli integration queue-status

# Force immediate sync
python -m moatmetrics.cli integration sync-now --system=datto
```

**Common Causes:**
- High API latency
- Large data volumes
- Network connectivity issues
- Target system maintenance

**Solutions:**
- Implement parallel sync processes
- Add incremental sync checkpoints
- Configure retry mechanisms
- Monitor target system status

#### **3. Data Quality Issues**

```python path=null start=null
# Data validation and cleanup
from moatmetrics.integrations.validation import DataValidator

validator = DataValidator()

# Validate imported data
validation_results = validator.validate_dataset(
    dataset='clients',
    rules=['required_fields', 'data_types', 'business_rules']
)

# Review and fix data quality issues
for issue in validation_results.issues:
    print(f"Issue: {issue.description}")
    print(f"Fix: {issue.suggested_fix}")
```

### **Logging & Alerts**

#### **Integration Logs**

```bash path=null start=null
# View integration logs
tail -f /var/log/moatmetrics/integrations.log

# Filter by integration type
grep "connectwise" /var/log/moatmetrics/integrations.log
```

#### **Alert Configuration**

```yaml
# Integration alert rules
alerts:
  sync_failure:
    condition: "failed_syncs > 3 in 1 hour"
    action: "email_admin"
    
  api_rate_limit:
    condition: "rate_limit_usage > 90%"
    action: "slow_down_requests"
    
  data_quality:
    condition: "validation_errors > 10%"
    action: "pause_sync_and_alert"
```

---

## 🔒 **Security & Compliance**

### **Data Protection**

#### **Encryption**
- **In Transit**: TLS 1.3 for all API communications
- **At Rest**: AES-256 encryption for stored credentials
- **Local Processing**: No data transmitted to external analytics services

#### **Access Control**
```python path=null start=null
# Role-based access for integrations
integration_roles = {
    'integration_admin': [
        'create_integration',
        'modify_integration',
        'delete_integration',
        'view_credentials'
    ],
    'integration_user': [
        'view_integration_status',
        'trigger_sync',
        'view_sync_logs'
    ],
    'read_only': [
        'view_integration_status'
    ]
}
```

### **Compliance Features**

#### **Audit Trail**
```python path=null start=null
# Integration audit logging
audit_events = [
    'integration_created',
    'credentials_updated',
    'sync_initiated',
    'data_accessed',
    'configuration_changed'
]

# Audit log entry example
{
    'timestamp': '2025-09-04T10:30:00Z',
    'user_id': 'admin@msp.com',
    'action': 'integration_created',
    'resource': 'connectwise_integration',
    'ip_address': '192.168.1.100',
    'user_agent': 'MoatMetrics/1.0.0'
}
```

#### **Data Retention**
```yaml
# Data retention policies
retention_policies:
  integration_logs: "90 days"
  sync_history: "1 year"
  audit_trail: "7 years"
  credentials: "encrypted_indefinite"
```

---

## 📝 **Integration Templates**

### **Custom System Integration**

```python path=null start=null
# Template for custom system integration
from moatmetrics.integrations.base import BaseIntegration

class CustomSystemIntegration(BaseIntegration):
    """Template for integrating custom systems"""
    
    def __init__(self, api_url, api_key):
        super().__init__()
        self.api_url = api_url
        self.api_key = api_key
    
    def test_connection(self) -> bool:
        """Test API connectivity"""
        try:
            response = requests.get(f"{self.api_url}/health", 
                                  headers=self._get_headers())
            return response.status_code == 200
        except Exception:
            return False
    
    def sync_clients(self) -> List[Client]:
        """Sync client data from system"""
        response = self._api_request('GET', '/clients')
        return [self._map_client_data(item) for item in response.json()]
    
    def _map_client_data(self, raw_data: dict) -> Client:
        """Transform raw API data to MoatMetrics client model"""
        return Client(
            client_id=raw_data['id'],
            name=raw_data['company_name'],
            monthly_fee=Decimal(raw_data['monthly_revenue']),
            # ... additional mapping
        )
```

### **File Import Template**

```python path=null start=null
# Template for file-based imports
from moatmetrics.integrations.file_import import CSVImporter

# Define custom CSV mapping
csv_config = {
    'file_path': 'custom_export.csv',
    'encoding': 'utf-8',
    'delimiter': ',',
    'has_header': True,
    'field_mapping': {
        'Client ID': 'client_id',
        'Company Name': 'name',
        'Monthly Fee': 'monthly_fee',
        'Start Date': 'contract_start'
    },
    'data_transforms': {
        'monthly_fee': lambda x: float(x.replace('$', '')),
        'contract_start': lambda x: datetime.strptime(x, '%Y-%m-%d')
    }
}

# Execute import
importer = CSVImporter()
result = importer.import_data(csv_config)
```

---

## 🚀 **Advanced Integration Scenarios**

### **Multi-PSA Environment**

For MSPs using multiple PSA systems:

```python path=null start=null
# Multi-PSA configuration
multi_psa_config = {
    'primary_psa': 'connectwise',
    'secondary_psa': 'autotask',
    'conflict_resolution': 'primary_wins',
    'client_matching': {
        'method': 'email_domain',
        'confidence_threshold': 0.9
    }
}
```

### **Data Warehouse Integration**

For enterprises with existing data warehouses:

```python path=null start=null
# Data warehouse export configuration
warehouse_config = {
    'export_format': 'parquet',
    'export_frequency': 'daily',
    'destination': 's3://your-bucket/moatmetrics-exports/',
    'partitioning': ['year', 'month', 'day'],
    'compression': 'snappy'
}
```

### **Custom Analytics Pipeline**

```python path=null start=null
# Custom analytics pipeline integration
from moatmetrics.analytics.pipeline import AnalyticsPipeline

pipeline = AnalyticsPipeline()

# Add custom transformation step
@pipeline.transform_step
def custom_profitability_calc(data):
    """Custom profitability calculation"""
    data['custom_margin'] = (data['revenue'] - data['costs']) / data['revenue']
    return data

# Add custom aggregation
@pipeline.aggregation_step
def monthly_summaries(data):
    """Generate monthly client summaries"""
    return data.groupby(['client_id', 'month']).agg({
        'revenue': 'sum',
        'costs': 'sum',
        'custom_margin': 'mean'
    })
```

---

## 📋 **Testing & Validation**

### **Integration Testing Suite**

```bash path=null start=null
# Run integration test suite
python -m pytest tests/integrations/ -v

# Test specific integration
python -m pytest tests/integrations/test_connectwise.py -v

# Test with live API (requires credentials)
python -m pytest tests/integrations/test_live_apis.py --live-apis
```

### **Data Validation Tests**

```python path=null start=null
# Data validation test example
def test_client_data_quality():
    """Test imported client data quality"""
    clients = get_imported_clients()
    
    # Validate required fields
    assert all(c.client_id for c in clients)
    assert all(c.name for c in clients)
    assert all(c.monthly_fee >= 0 for c in clients)
    
    # Validate data consistency
    assert len(set(c.client_id for c in clients)) == len(clients)  # Unique IDs
    
    # Validate business rules
    managed_clients = [c for c in clients if c.contract_type == 'managed']
    assert all(c.monthly_fee > 0 for c in managed_clients)
```

### **Performance Testing**

```bash path=null start=null
# Performance test for large datasets
python -m moatmetrics.test.performance \
    --integration=connectwise \
    --clients=1000 \
    --time_entries=50000 \
    --duration=300
```

---

## 🛡️ **Best Practices**

### **Security Best Practices**

1. **Credential Management**
   - Use environment variables for sensitive data
   - Rotate API keys quarterly
   - Monitor for credential leaks
   - Implement principle of least privilege

2. **Network Security**
   - Whitelist IP addresses where possible
   - Use VPN connections for cloud integrations
   - Implement certificate pinning
   - Monitor for suspicious network activity

3. **Data Protection**
   - Encrypt sensitive data at rest
   - Use HTTPS for all communications
   - Implement data masking for development
   - Regular security audits

### **Performance Best Practices**

1. **Optimization Strategies**
   - Implement incremental syncs
   - Use parallel processing where safe
   - Cache frequently accessed data
   - Monitor and optimize query performance

2. **Resource Management**
   - Set appropriate rate limits
   - Implement circuit breakers
   - Monitor memory and CPU usage
   - Plan for peak load scenarios

### **Operational Best Practices**

1. **Monitoring & Alerting**
   - Set up comprehensive monitoring
   - Configure meaningful alerts
   - Establish escalation procedures
   - Regular health check reviews

2. **Documentation & Maintenance**
   - Keep integration documentation current
   - Document all customizations
   - Regular testing of backup procedures
   - Version control for integration configs

---

## 📞 **Support & Resources**

### **Getting Help**

#### **Documentation Resources**
- **API Reference**: Complete endpoint documentation
- **Integration Examples**: Sample code for common scenarios
- **Troubleshooting Guide**: Common issues and solutions
- **Best Practices**: Recommendations for optimal setup

#### **Support Channels**
- **Technical Support**: support@moatmetrics.com
- **Integration Help**: integrations@moatmetrics.com
- **Community Forum**: community.moatmetrics.com
- **Documentation**: docs.moatmetrics.com

#### **Professional Services**
- **Integration Consulting**: Custom integration development
- **Data Migration**: Professional data migration services
- **Training**: Team training and certification programs
- **Managed Setup**: White-glove integration setup service

### **Integration Request Process**

For systems not currently supported:

```bash path=null start=null
# Submit integration request
python -m moatmetrics.cli integration request \
    --system="Custom System Name" \
    --api-docs-url="https://api-docs-url.com" \
    --business-case="Brief justification" \
    --contact-email="your.email@company.com"
```

---

**This integration guide provides comprehensive instructions for connecting MoatMetrics with your existing MSP technology stack while maintaining security, privacy, and data integrity standards.**

---

**Document Status**: Active  
**Next Review**: October 1, 2025  
**Owner**: Engineering Team
