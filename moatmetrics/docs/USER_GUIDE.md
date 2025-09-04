# User Guide

## 👥 **MoatMetrics User Manual**

Complete guide for MSP professionals to effectively use MoatMetrics for business analytics and decision-making.

**Document Version**: 1.0.0  
**Last Updated**: September 4, 2025  
**Target Audience**: MSP Executives, Operations Managers, Financial Analysts

---

## 🚀 **Getting Started**

### **What is MoatMetrics?**

MoatMetrics is a privacy-first analytics platform specifically designed for Managed Service Providers (MSPs) to:
- **Analyze client profitability** and identify high/low-value relationships
- **Optimize license utilization** and reduce software waste
- **Track resource efficiency** and improve staff productivity
- **Make data-driven decisions** with confidence scoring and explanations

### **Key Benefits**
- ✅ **Privacy-First**: All data stays on your systems
- ✅ **MSP-Focused**: Built specifically for service providers
- ✅ **Easy to Use**: 15-minute setup with immediate insights
- ✅ **Explainable Results**: Clear explanations for all analytics
- ✅ **Confident Decisions**: Reliability scoring for every result

---

## 📊 **Core Workflows**

### **Workflow 1: Client Profitability Analysis**

This workflow helps you identify your most and least profitable clients.

#### **Step 1: Prepare Your Data**

You'll need these data files in CSV format:

##### **Clients Data (`clients.csv`)**
```csv
client_name,industry,status,contract_value
TechCorp Solutions,Technology,Active,50000
HealthCare Plus,Healthcare,Active,75000
RetailMart Inc,Retail,Active,30000
```

##### **Invoice Data (`invoices.csv`)**
```csv
invoice_id,client_name,amount,date,status
INV-2025-001,TechCorp Solutions,12500,2025-08-15,Paid
INV-2025-002,HealthCare Plus,8750,2025-08-20,Paid
INV-2025-003,RetailMart Inc,5200,2025-08-22,Pending
```

##### **Time Logs (`time_logs.csv`)**
```csv
staff_name,client_name,hours,rate,billable,date
John Smith,TechCorp Solutions,8,75,True,2025-08-15
Jane Doe,HealthCare Plus,6,80,True,2025-08-15
Mike Johnson,RetailMart Inc,10,70,True,2025-08-22
```

#### **Step 2: Upload Data via Web Interface**

1. **Open MoatMetrics**: Navigate to `http://localhost:8000/docs`
2. **Authenticate**: Use your admin credentials
3. **Upload Clients**: 
   - Click on `/api/upload/clients`
   - Click "Try it out"
   - Upload your `clients.csv` file
   - Click "Execute"
4. **Upload Invoices**: Repeat process with `invoices.csv`
5. **Upload Time Logs**: Repeat process with `time_logs.csv`

#### **Step 3: Run Analytics**

1. **Navigate to Analytics**: Click on `/api/analytics/run`
2. **Configure Analysis**:
   ```json
   {
     "metric_types": ["profitability"],
     "include_explanations": true,
     "confidence_threshold": 0.7
   }
   ```
3. **Execute**: Click "Execute" button
4. **Copy Analysis ID**: Note the `analysis_id` from the response

#### **Step 4: Review Results**

1. **Get Results**: Use `/api/analytics/results/{analysis_id}`
2. **Interpret Profit Margins**:
   - **>20%**: Excellent profitability
   - **10-20%**: Good profitability  
   - **5-10%**: Moderate profitability
   - **<5%**: Poor profitability (review needed)

#### **Step 5: Business Actions**

Based on your results:
- **High-Profit Clients**: Consider expanding services or raising rates
- **Low-Profit Clients**: Analyze costs, renegotiate contracts, or improve efficiency
- **Flagged Results**: Review confidence explanations and validate data

### **Workflow 2: License Optimization**

Identify wasted software licenses and cost-saving opportunities.

#### **Step 1: Prepare License Data**

##### **License Data (`licenses.csv`)**
```csv
client_name,product_name,seats_purchased,seats_used,cost_per_seat,status
TechCorp Solutions,Microsoft 365,50,32,12,Active
TechCorp Solutions,Adobe Creative Suite,10,8,60,Active
HealthCare Plus,Salesforce Professional,25,15,100,Active
```

#### **Step 2: Upload and Analyze**

1. **Upload License Data**: Follow upload process for `licenses.csv`
2. **Run License Analysis**:
   ```json
   {
     "metric_types": ["license_efficiency"],
     "include_explanations": true
   }
   ```

#### **Step 3: Interpret License Results**

**Utilization Levels:**
- **>80%**: Optimal utilization
- **50-80%**: Moderate utilization  
- **30-50%**: Underutilized (review recommended)
- **<30%**: Critical waste (immediate action needed)

**Example Result:**
```json
{
  "client_name": "TechCorp Solutions",
  "product_name": "Microsoft 365",
  "utilization_rate": 64.0,
  "seats_wasted": 18,
  "waste_amount": 216,
  "recommendation": "Review with client for seat reduction or find users for unused licenses"
}
```

#### **Step 4: Cost Optimization Actions**

- **Reduce Seats**: Contact clients about unused licenses
- **Reallocate**: Move licenses between clients
- **Renegotiate**: Better pricing with vendors
- **Switch Plans**: Downgrade to more appropriate tiers

### **Workflow 3: Resource Utilization Analysis**

Track staff productivity and identify capacity planning needs.

#### **Step 1: Comprehensive Time Tracking Data**

Ensure your `time_logs.csv` includes all staff activities:

```csv
staff_name,client_name,hours,rate,billable,date,project,task_type
John Smith,TechCorp Solutions,8,75,True,2025-08-15,Server Maintenance,Billable
John Smith,Internal,2,75,False,2025-08-15,Training,Non-Billable
Jane Doe,HealthCare Plus,6,80,True,2025-08-15,Security Audit,Billable
Jane Doe,Internal,1,80,False,2025-08-15,Administrative,Non-Billable
```

#### **Step 2: Run Resource Analysis**

```json
{
  "metric_types": ["resource_utilization"],
  "include_explanations": true,
  "start_date": "2025-08-01",
  "end_date": "2025-08-31"
}
```

#### **Step 3: Interpret Resource Results**

**Utilization Benchmarks:**
- **>100%**: Over-utilization (burnout risk)
- **80-100%**: High utilization (optimal)
- **60-80%**: Moderate utilization
- **<60%**: Under-utilization (capacity available)

**Example Result:**
```json
{
  "staff_name": "John Smith",
  "utilization_rate": 95.0,
  "billable_percentage": 85.0,
  "recommendation": "Consider hiring additional staff or redistributing workload"
}
```

#### **Step 4: Capacity Planning**

- **Over-Utilized**: Hire additional staff or redistribute work
- **Under-Utilized**: Take on more clients or train in new skills
- **Optimal**: Maintain current staffing levels

---

## 🎯 **Advanced Features**

### **Confidence Scoring System**

MoatMetrics provides confidence scores (0.1-1.0) for every result:

#### **Understanding Confidence Levels**
- **High (0.9-1.0)**: 🟢 **Trust completely** - Act on these results
- **Medium (0.7-0.89)**: 🟡 **Generally reliable** - Safe to use for decisions
- **Low (0.5-0.69)**: 🟠 **Use with caution** - Validate before major decisions
- **Very Low (<0.5)**: 🔴 **Requires review** - Investigate data quality

#### **What Affects Confidence?**
1. **Data Completeness**: Missing data reduces confidence
2. **Data Quality**: Zeros, nulls, or outliers lower confidence
3. **Consistency**: Mismatched client names between files
4. **Recency**: Older data may be less reliable

#### **Improving Confidence Scores**
1. **Complete Data**: Ensure all required fields are filled
2. **Consistent Naming**: Use identical client names across all files
3. **Regular Updates**: Upload data frequently
4. **Validate Inputs**: Check data before uploading

### **Human-in-the-Loop Reviews**

When confidence scores are below your threshold, results are flagged for review.

#### **Review Process**
1. **Automatic Flagging**: Low-confidence results require approval
2. **Review Interface**: Access via `/api/governance/reviews`
3. **Investigation**: Check data sources and business context
4. **Decision**: Approve, reject, or request more data

#### **Review Criteria**
- **Low Confidence**: Below configured threshold (default: 0.7)
- **Business Rules**: Specific triggers (e.g., negative profit margins)
- **Data Anomalies**: Unusual patterns or outliers

### **Explanation System**

Every result includes human-readable explanations:

#### **Example Explanations**
```
"Strong profit margin of 24.5% indicates healthy client relationship. 
Based on $50,000 revenue and $37,750 in labor costs. 
Confidence: 85% (high data quality, minor time tracking gaps)"
```

```
"License utilization at 64% shows moderate efficiency. 
18 unused Microsoft 365 seats represent $216/month waste. 
Consider client seat optimization. Confidence: 92%"
```

```
"Staff utilization at 95% indicates high productivity but potential burnout risk. 
85% billable ratio is excellent. Consider capacity planning. 
Confidence: 78% (some time log gaps detected)"
```

---

## 📈 **Interpreting Results**

### **Profitability Analysis Results**

#### **Key Metrics Explained**

**Profit Margin**: `(Revenue - Costs) / Revenue * 100`
- **What it means**: Percentage of revenue that becomes profit
- **Good range**: 15-30% for most MSPs
- **Red flags**: <5% (unprofitable) or >50% (may indicate missing costs)

**Revenue**: Total invoiced amount for the client
- **Calculation**: Sum of all paid and pending invoices
- **Considerations**: Excludes unpaid/cancelled invoices

**Costs**: Labor costs based on time tracking
- **Calculation**: `Hours * Hourly Rate` for all staff time
- **Limitations**: Only includes tracked time, not overhead costs

#### **Business Decision Framework**

**For High-Profit Clients (>20% margin):**
1. **Expand Services**: Offer additional services
2. **Case Studies**: Use as reference for sales
3. **Retention Focus**: Ensure high satisfaction
4. **Rate Optimization**: Consider selective rate increases

**For Medium-Profit Clients (10-20% margin):**
1. **Efficiency Improvements**: Streamline processes
2. **Service Mix**: Optimize service offerings
3. **Contract Review**: Renegotiate terms if needed
4. **Monitoring**: Track trends over time

**For Low-Profit Clients (<10% margin):**
1. **Cost Analysis**: Identify inefficiencies
2. **Scope Review**: Ensure work scope is clear
3. **Rate Adjustment**: Consider price increases
4. **Exit Strategy**: Consider ending relationship if unprofitable

### **License Efficiency Results**

#### **Optimization Strategies**

**Critical Waste (<30% utilization):**
1. **Immediate Review**: Contact client within 1 week
2. **Seat Reduction**: Reduce licenses by 50% or more
3. **Alternative Solutions**: Consider cheaper alternatives
4. **Contract Renegotiation**: Use as leverage for better terms

**Moderate Waste (30-50% utilization):**
1. **Quarterly Review**: Schedule regular optimization meetings
2. **User Training**: Help client maximize usage
3. **Gradual Reduction**: Reduce seats by 20-30%
4. **Usage Monitoring**: Track improvements over time

**Optimal Usage (>80% utilization):**
1. **Expansion Opportunity**: Suggest additional seats
2. **Upselling**: Recommend higher-tier plans
3. **Success Story**: Use as positive client case study

#### **Cost Savings Calculation**

MoatMetrics automatically calculates potential savings:
```
Monthly Waste = Unused Seats × Cost per Seat
Annual Savings = Monthly Waste × 12
ROI Impact = Annual Savings / Total Contract Value
```

### **Resource Utilization Results**

#### **Staff Performance Analysis**

**Utilization Rate**: `Actual Hours / Expected Hours * 100`
- **Expected Hours**: Typically 40 hours/week
- **Actual Hours**: From time tracking data
- **Optimal Range**: 80-100% for billable staff

**Billable Percentage**: `Billable Hours / Total Hours * 100`
- **Industry Benchmark**: 70-80% for most MSPs
- **High Performance**: >85%
- **Target Range**: Varies by role and seniority

#### **Capacity Planning Insights**

**Over-Utilization (>100%):**
- **Risk**: Staff burnout, quality issues
- **Actions**: Hire additional staff, redistribute workload
- **Monitoring**: Track stress indicators, quality metrics

**Under-Utilization (<70%):**
- **Opportunity**: Take on more clients, expand services
- **Actions**: Sales focus, staff training, process improvement
- **Considerations**: May be seasonal or role-specific

---

## 🎯 **Practical Examples**

### **Example 1: Identifying Unprofitable Clients**

**Scenario**: Operations Manager wants to improve overall profitability

#### **Data Upload**
Upload September 2025 data for all clients:
- 47 clients in `clients.csv`
- 234 invoices in `invoices.csv`
- 1,156 time log entries in `time_logs.csv`

#### **Analytics Request**
```json
{
  "metric_types": ["profitability"],
  "start_date": "2025-09-01",
  "end_date": "2025-09-30",
  "include_explanations": true,
  "confidence_threshold": 0.8
}
```

#### **Key Results**
```json
{
  "ClientA": {
    "profit_margin": 32.5,
    "confidence_score": 0.92,
    "explanation": "Excellent profitability at 32.5% margin",
    "requires_review": false
  },
  "ClientB": {
    "profit_margin": 2.8,
    "confidence_score": 0.85,
    "explanation": "Low profitability at 2.8% margin requires review",
    "requires_review": true
  }
}
```

#### **Business Actions Taken**
1. **ClientA**: Expanded service contract by 20%
2. **ClientB**: Identified inefficient processes, improved margin to 15%
3. **Overall Impact**: Portfolio profitability increased from 18% to 23%

### **Example 2: Software License Optimization**

**Scenario**: Financial Analyst needs to reduce software costs

#### **Data Preparation**
License data for Q3 2025:
- 23 different software products
- 12 clients with license waste >30%
- Total monthly license costs: $18,500

#### **Analysis Results**
```json
{
  "Microsoft 365": {
    "total_seats_purchased": 200,
    "total_seats_used": 156,
    "utilization_rate": 78.0,
    "waste_amount": 528,
    "recommendation": "Moderate waste - review quarterly"
  },
  "Adobe Creative Suite": {
    "total_seats_purchased": 45,
    "total_seats_used": 12,
    "utilization_rate": 26.7,
    "waste_amount": 1980,
    "recommendation": "Critical waste - immediate action required"
  }
}
```

#### **Optimization Results**
1. **Adobe Creative Suite**: Reduced from 45 to 15 seats
2. **Monthly Savings**: $1,800 (30 seats × $60/seat)
3. **Annual Impact**: $21,600 saved
4. **Client Satisfaction**: Improved through cost optimization consulting

### **Example 3: Resource Planning**

**Scenario**: CEO planning for Q4 2025 growth

#### **Current Team Analysis**
- 8 technical staff members
- Average utilization: 87%
- Average billable percentage: 82%
- Target growth: 25% revenue increase

#### **Analytics Results**
```json
{
  "team_summary": {
    "avg_utilization_rate": 87.0,
    "avg_billable_percentage": 82.0,
    "capacity_available": "13% additional capacity",
    "high_utilization_staff": ["John Smith", "Jane Doe"],
    "available_capacity_staff": ["Mike Johnson", "Sarah Wilson"]
  }
}
```

#### **Staffing Plan**
1. **Current Capacity**: Can handle ~13% more work
2. **Growth Target**: 25% requires additional hiring
3. **Hiring Plan**: Add 2 technical staff members
4. **Timeline**: Hire by October for Q4 onboarding

---

## 📊 **Data Management Best Practices**

### **Data Quality Guidelines**

#### **Required Fields**
Ensure these fields are always populated:
- **Client Name**: Must be identical across all files
- **Amounts**: No negative values (use 0 for refunds/credits)
- **Dates**: Use YYYY-MM-DD format consistently
- **Status**: Use standardized values (Active, Inactive, Paid, Pending)

#### **Data Validation Checklist**

Before uploading, verify:
- [ ] **Client names** are identical across all CSV files
- [ ] **Date formats** are consistent (YYYY-MM-DD)
- [ ] **Numeric fields** contain only numbers (no currency symbols)
- [ ] **Required fields** are not empty
- [ ] **File encoding** is UTF-8
- [ ] **Headers match** expected column names

#### **Common Data Issues**

**Issue**: Client names don't match between files
```csv
# In clients.csv
TechCorp Solutions

# In invoices.csv  
TechCorp Solution   # Missing 's'
```
**Solution**: Use Find/Replace in Excel to standardize names

**Issue**: Currency symbols in amounts
```csv
amount
$12,500.00    # Wrong
12500         # Correct
```
**Solution**: Remove currency symbols and commas

**Issue**: Inconsistent date formats
```csv
date
08/15/2025    # Wrong
2025-08-15    # Correct
```
**Solution**: Use Excel's Format Cells > Date > YYYY-MM-DD

### **Data Organization Tips**

#### **File Naming Convention**
```
clients_YYYY_MM_DD.csv
invoices_YYYY_MM_DD.csv
time_logs_YYYY_MM_DD.csv
licenses_YYYY_MM_DD.csv
```

#### **Monthly Upload Process**
1. **Week 1**: Prepare and clean data files
2. **Week 2**: Upload data and run initial analytics
3. **Week 3**: Review flagged results and validate insights
4. **Week 4**: Present findings to stakeholders and plan actions

#### **Data Retention**
- **Keep Raw Files**: Store original CSVs for auditing
- **Version Control**: Use snapshot names for tracking
- **Backup Strategy**: Regular backups of both files and database

---

## 💡 **Tips & Best Practices**

### **Analytics Best Practices**

#### **Frequency Recommendations**
- **Daily**: For operational metrics during busy periods
- **Weekly**: For resource utilization tracking
- **Monthly**: For profitability and license optimization
- **Quarterly**: For comprehensive business reviews

#### **Confidence Score Guidelines**
- **>0.9**: Use for strategic decisions
- **0.7-0.9**: Good for operational decisions
- **0.5-0.7**: Validate before acting
- **<0.5**: Investigate data quality issues

#### **Review Thresholds**
Customize review thresholds based on your business:
- **Conservative**: 0.8 (fewer false positives)
- **Standard**: 0.7 (balanced approach)
- **Aggressive**: 0.6 (catch more potential issues)

### **Performance Optimization**

#### **Large Dataset Handling**
For files with >10,000 records:
1. **Split Files**: Process in smaller chunks
2. **Date Ranges**: Limit analysis to specific periods
3. **Selective Analysis**: Focus on specific metrics
4. **Batch Processing**: Upload during off-peak hours

#### **Memory Management**
- **Close Browser Tabs**: Keep only necessary documentation open
- **Restart Periodically**: Daily restart for optimal performance
- **Monitor Resources**: Check system resource usage

### **Security Best Practices**

#### **Data Protection**
1. **Local Processing**: All data stays on your systems
2. **Access Control**: Use role-based permissions
3. **Audit Trails**: All actions are logged
4. **Backup Strategy**: Regular backups with encryption

#### **Privacy Compliance**
- **GDPR Ready**: Built-in data governance features
- **Client Consent**: Document analytics usage in client agreements
- **Data Minimization**: Only upload necessary data
- **Retention Policies**: Implement data retention schedules

---

## 🔄 **Routine Maintenance**

### **Daily Tasks**
- [ ] Check system health: `curl http://localhost:8000/health`
- [ ] Monitor disk space: `df -h`
- [ ] Review error logs: `tail logs/error.log`

### **Weekly Tasks**
- [ ] Upload current week's data
- [ ] Run analytics for operational insights
- [ ] Review flagged results
- [ ] Update client information as needed

### **Monthly Tasks**
- [ ] Comprehensive profitability analysis
- [ ] License optimization review
- [ ] Performance analytics
- [ ] Data quality assessment
- [ ] System backup verification

### **Quarterly Tasks**
- [ ] Strategic business review
- [ ] System performance optimization
- [ ] Security audit
- [ ] Documentation updates
- [ ] Staff training refresh

---

## 📋 **Templates & Checklists**

### **Data Upload Checklist**

#### **Before Upload**
- [ ] Files saved as CSV (UTF-8 encoding)
- [ ] Column headers match exactly
- [ ] Client names consistent across files
- [ ] No special characters in numeric fields
- [ ] Date format is YYYY-MM-DD
- [ ] Required fields are not empty
- [ ] File size under 100MB

#### **After Upload**
- [ ] Check upload success message
- [ ] Verify record counts match expectations
- [ ] Review any validation warnings
- [ ] Check data quality score (target: >0.9)
- [ ] Run test analytics to verify data

### **Monthly Analytics Checklist**

#### **Preparation**
- [ ] All data uploaded for the month
- [ ] Client list is up to date
- [ ] Time tracking data is complete
- [ ] License information is current

#### **Analysis**
- [ ] Run profitability analysis
- [ ] Execute license efficiency check
- [ ] Analyze resource utilization
- [ ] Review confidence scores
- [ ] Investigate flagged results

#### **Review & Action**
- [ ] Validate low-confidence results
- [ ] Document key insights
- [ ] Create action items for optimization
- [ ] Schedule client discussions as needed
- [ ] Update strategic plans based on findings

---

## 🎓 **Training & Support**

### **User Training Program**

#### **New User Onboarding (2 hours)**
1. **Overview Session** (30 minutes): MoatMetrics concepts and benefits
2. **Hands-On Training** (60 minutes): Data upload and analytics walkthrough
3. **Practice Session** (30 minutes): Real data analysis with guidance

#### **Advanced User Training (1 hour)**
1. **Advanced Features** (20 minutes): Confidence scoring and review workflows
2. **Optimization Techniques** (20 minutes): Data quality and performance
3. **Business Integration** (20 minutes): Incorporating insights into operations

#### **Administrator Training (1.5 hours)**
1. **System Administration** (30 minutes): Configuration and maintenance
2. **User Management** (30 minutes): Roles and permissions
3. **Troubleshooting** (30 minutes): Common issues and solutions

### **Support Resources**

#### **Self-Service Resources**
- **Documentation**: Complete user guides and API reference
- **Video Tutorials**: Step-by-step workflow demonstrations
- **FAQ**: Common questions and solutions
- **Community Forum**: User community discussions

#### **Professional Support**
- **Email Support**: help@moatmetrics.com
- **Training Sessions**: Customized training for your team
- **Consultation Services**: Business process optimization
- **Premium Support**: Priority response for enterprise customers

---

## 📞 **Getting Help**

### **Before Contacting Support**

1. **Check Documentation**: Most issues are covered in this guide
2. **Search Known Issues**: Review troubleshooting guide
3. **Check System Health**: Run basic diagnostics
4. **Gather Information**: Collect logs and error messages

### **Support Request Template**

```
Subject: [PRIORITY] Brief description of issue

Environment:
- Operating System:
- MoatMetrics Version:
- Browser (if applicable):
- Data Size:

Issue Description:
[Detailed description of the problem]

Steps to Reproduce:
1. 
2. 
3. 

Expected Behavior:
[What should happen]

Actual Behavior:
[What actually happens]

Error Messages:
[Copy exact error messages]

Files Involved:
[List relevant CSV files or data]

Troubleshooting Attempted:
[What you've already tried]

Business Impact:
[How this affects your operations]
```

### **Response Time Expectations**

| **Priority** | **Description** | **Response Time** | **Resolution Time** |
|---|---|---|---|
| **Critical** | Production down, data corruption | 1 hour | 4 hours |
| **High** | Major functionality impaired | 4 hours | 24 hours |
| **Medium** | Minor functionality issues | 24 hours | 3 business days |
| **Low** | Questions, enhancements | 3 business days | As scheduled |

---

**This user guide provides comprehensive instructions for effectively using MoatMetrics to optimize your MSP business operations. For additional support, refer to the troubleshooting guide or contact our support team.** 🚀

---

**Document Status**: Production Ready  
**Next Review**: October 1, 2025  
**Maintainer**: Customer Success Team
