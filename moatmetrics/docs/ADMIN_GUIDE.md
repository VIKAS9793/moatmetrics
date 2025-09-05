# MoatMetrics Administrator's Guide

## System Architecture

MoatMetrics is built on a modern microservices architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Streamlit UI   │◄───►│  FastAPI Backend │◄───►│   MongoDB       │
│  (Frontend)     │     │  (API Layer)    │     │  (Database)     │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## API Documentation

Access the interactive API documentation at `http://your-server:8000/docs`

![Swagger UI](./image/assets/Swagger%20UI%201.png)

## User Management

### Adding New Users

1. Navigate to the Admin Panel
2. Click "Add User"
3. Fill in user details
4. Assign appropriate roles:
   - **Admin**: Full system access
   - **Manager**: Can manage clients and view reports
   - **Viewer**: Read-only access

### Managing Permissions

Permissions are managed through role-based access control (RBAC):

```yaml
roles:
  admin:
    - users:create
    - users:read
    - users:update
    - users:delete
    - reports:generate
    - data:import
    - settings:manage
  
  manager:
    - users:read
    - reports:generate
    - data:import

  viewer:
    - dashboard:view
    - reports:view
```

## Data Management

### Data Import

Supported formats:
- CSV
- Excel (.xlsx, .xls)

### Data Validation

All imported data is validated against schemas. Example schema for client data:

```json
{
  "client_id": "string",
  "name": "string",
  "status": "active|inactive|prospect",
  "contact_email": "email",
  "start_date": "date"
}
```

## Backup and Recovery

### Automated Backups

Configure in `.env`:
```
BACKUP_ENABLED=true
BACKUP_SCHEDULE=0 0 * * *  # Daily at midnight
BACKUP_RETENTION_DAYS=30
```

### Manual Backup

```bash
python manage.py backup --output=backup_$(date +%Y%m%d).json
```

### Restore from Backup

```bash
python manage.py restore backup_20230901.json
```

## Monitoring and Logs

### Accessing Logs

Logs are stored in `/var/log/moatmetrics/` with the following structure:
- `app.log`: Application logs
- `api.log`: API request/response logs
- `error.log`: Error logs

### Monitoring Endpoints

- Health Check: `GET /health`
- Metrics: `GET /metrics` (Prometheus format)
- System Info: `GET /system/info`

## Security

### SSL/TLS Configuration

1. Obtain SSL certificates (e.g., from Let's Encrypt)
2. Update Nginx configuration:
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8501;
    }
}
```

### Security Best Practices

1. Enable 2FA for all admin accounts
2. Regularly rotate API keys
3. Keep the system updated
4. Regular security audits

## Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Verify the API server is running
   - Check network connectivity
   - Verify CORS settings

2. **Data Import Failures**
   - Check file format and size
   - Verify required fields in the import file
   - Check server logs for validation errors

3. **Performance Issues**
   - Check database indexes
   - Monitor server resources
   - Review query performance

## Support

For technical support, please contact:
- Email: dev-support@moatmetrics.com
- Slack: #moatmetrics-support
- Documentation: [GitHub Wiki](https://github.com/VIKAS9793/moatmetrics/wiki)
