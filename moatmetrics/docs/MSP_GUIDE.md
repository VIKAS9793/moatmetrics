# MoatMetrics for MSPs

## Overview
MoatMetrics is a powerful analytics and monitoring platform designed specifically for Managed Service Providers (MSPs) to track client profitability, resource utilization, and license management.

## Key Features

### 1. Client Management
- Centralized dashboard for all client accounts
- Real-time monitoring of client health and performance
- Profitability analysis per client

### 2. Resource Utilization
- Track team productivity and allocation
- Monitor system and application performance
- Identify optimization opportunities

### 3. License Management
- Centralized view of all software licenses
- Usage tracking and optimization
- Cost analysis and savings opportunities

## Getting Started

### Prerequisites
- Python 3.8+
- Docker (for containerized deployment)
- MongoDB (for data storage)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/VIKAS9793/moatmetrics.git
cd moatmetrics
```

![Repository Structure](../image/assets/Admin%20Panel.png)

2. Set up the environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

3. Configure the application:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Start the services:
```bash
# Start the backend API
uvicorn src.api.main:app --reload

# In a new terminal, start the frontend
streamlit run demo_ui.py
```

## User Guides

### For Technical Staff
- [API Documentation](API.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Troubleshooting](TROUBLESHOOTING.md)

### For Non-Technical Users
- [Getting Started Guide](GETTING_STARTED.md)
- [User Guide](USER_GUIDE.md) - Complete user documentation
- [Admin Guide](ADMIN_GUIDE.md) - Administrator features

## Support
For support, please contact:
- Email: support@moatmetrics.com
- Phone: (555) 123-4567
- Documentation: [GitHub Wiki](https://github.com/VIKAS9793/moatmetrics/wiki)
