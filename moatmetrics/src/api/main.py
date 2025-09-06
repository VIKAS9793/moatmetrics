"""
Main FastAPI application for MoatMetrics.

This module provides REST API endpoints for data ingestion, analytics,
reporting, and governance operations.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path
import os
import tempfile

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from loguru import logger

from ..utils.database import get_db_session, get_db_manager
from ..utils.schemas import (
    ClientCreate, ClientUpdate, ClientResponse,
    InvoiceCreate, InvoiceResponse,
    TimeLogCreate, TimeLogResponse,
    LicenseCreate, LicenseResponse,
    AnalyticsRequest, AnalyticsResultResponse,
    FileUploadRequest, FileUploadResponse,
    ReportRequest, ReportResponse,
    AuditLogResponse
)
from ..utils.config_loader import get_config
from ..utils.logging_config import setup_logging
from ..etl.csv_processor import CSVProcessor
from ..analytics.engine import AnalyticsEngine
from ..governance.policy_engine import PolicyEngine, Permission
from ..agent.report_generator import ReportGenerator

# Initialize logging
setup_logging()

# Get configuration
config = get_config()

# Create FastAPI application
app = FastAPI(
    title=config.app.name,
    version=config.app.version,
    description="Privacy-first, offline, explainable analytics platform for MSPs with AI capabilities",
    debug=config.app.debug
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.api.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logger for API
api_logger = logger.bind(module="api")


# Dependency for user authentication (simplified for prototype)
def get_current_user() -> Dict[str, str]:
    """Get current user (simplified for prototype)."""
    return {"username": "admin", "role": "admin"}


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint with AI status."""
    # Check AI system health
    ai_status = "not_initialized"
    ai_features = {
        "natural_language_queries": False,
        "enhanced_processing": False,
        "batch_analytics": False
    }
    
    try:
        # Try to import and check AI components
        from .ai_analytics import memory_manager, nl_analytics, enhanced_analytics
        if all([memory_manager, nl_analytics, enhanced_analytics]):
            ai_status = "operational"
            ai_features = {
                "natural_language_queries": True,
                "enhanced_processing": True,
                "batch_analytics": True
            }
        else:
            ai_status = "partially_initialized"
    except Exception as e:
        ai_status = f"error: {str(e)[:50]}"
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": config.app.version,
        "ai_analytics": ai_status,
        "features": {
            "core_analytics": True,
            "data_governance": True,
            "audit_trails": True,
            "role_based_access": True,
            "privacy_first": True,
            "offline_processing": True,
            **ai_features
        }
    }


# Client endpoints
@app.post("/api/clients", response_model=ClientResponse)
async def create_client(
    client: ClientCreate,
    db: Session = Depends(get_db_session),
    user: Dict = Depends(get_current_user)
):
    """Create a new client."""
    try:
        # Check permission
        policy_engine = PolicyEngine(db)
        allowed, reason = policy_engine.check_permission(user["role"], Permission.DATA_WRITE)
        if not allowed:
            raise HTTPException(status_code=403, detail=reason)
        
        # Create client in database
        from ..utils.database import Client
        db_client = Client(**client.model_dump())
        db.add(db_client)
        db.commit()
        db.refresh(db_client)
        
        return ClientResponse.model_validate(db_client)
        
    except Exception as e:
        api_logger.error(f"Failed to create client: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/clients", response_model=List[ClientResponse])
async def list_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db_session),
    user: Dict = Depends(get_current_user)
):
    """List all clients."""
    try:
        # Check permission
        policy_engine = PolicyEngine(db)
        allowed, reason = policy_engine.check_permission(user["role"], Permission.DATA_READ)
        if not allowed:
            raise HTTPException(status_code=403, detail=reason)
        
        from ..utils.database import Client
        clients = db.query(Client).offset(skip).limit(limit).all()
        
        return [ClientResponse.model_validate(c) for c in clients]
        
    except Exception as e:
        api_logger.error(f"Failed to list clients: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/clients/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: int,
    db: Session = Depends(get_db_session),
    user: Dict = Depends(get_current_user)
):
    """Get a specific client."""
    try:
        # Check permission
        policy_engine = PolicyEngine(db)
        allowed, reason = policy_engine.check_permission(user["role"], Permission.DATA_READ)
        if not allowed:
            raise HTTPException(status_code=403, detail=reason)
        
        from ..utils.database import Client
        client = db.query(Client).filter(Client.client_id == client_id).first()
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        return ClientResponse.model_validate(client)
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Failed to get client: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# File upload endpoint
@app.post("/api/upload/{data_type}", response_model=FileUploadResponse)
async def upload_file(
    data_type: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    validate_schema: bool = Query(True),
    create_snapshot: bool = Query(True),
    dry_run: bool = Query(False),
    db: Session = Depends(get_db_session),
    user: Dict = Depends(get_current_user)
):
    """Upload and process a CSV file."""
    try:
        # Validate data type
        valid_types = ["clients", "invoices", "time_logs", "licenses"]
        if data_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Invalid data type. Must be one of: {valid_types}")
        
        # Check permission
        policy_engine = PolicyEngine(db)
        allowed, reason = policy_engine.check_permission(user["role"], Permission.DATA_WRITE)
        if not allowed:
            raise HTTPException(status_code=403, detail=reason)
        
        # Check file extension
        if not file.filename.endswith(('.csv', '.xlsx')):
            raise HTTPException(status_code=400, detail="Only CSV and Excel files are supported")
        
        # Check data governance
        file_size_mb = file.size / (1024 * 1024) if hasattr(file, 'size') else 0
        file_ext = Path(file.filename).suffix.lstrip('.')
        
        allowed, reason = policy_engine.enforce_data_governance(
            action="upload",
            data_type=data_type,
            file_size_mb=file_size_mb,
            file_type=file_ext
        )
        
        if not allowed:
            raise HTTPException(status_code=400, detail=reason)
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = Path(tmp.name)
        
        # Process file
        processor = CSVProcessor(db)
        result = processor.process_file(
            file_path=tmp_path,
            data_type=data_type,
            validate_schema=validate_schema,
            create_snapshot=create_snapshot,
            dry_run=dry_run,
            actor=user["username"]
        )
        
        # Clean up temp file
        try:
            os.unlink(tmp_path)
        except:
            pass
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Failed to process upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Analytics endpoints
@app.post("/api/analytics/run")
async def run_analytics(
    request: AnalyticsRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
    user: Dict = Depends(get_current_user)
):
    """Run analytics computations."""
    try:
        # Check permission
        policy_engine = PolicyEngine(db)
        allowed, reason = policy_engine.check_permission(user["role"], Permission.ANALYTICS_RUN)
        if not allowed:
            raise HTTPException(status_code=403, detail=reason)
        
        # Run analytics
        engine = AnalyticsEngine(db)
        results = engine.run_analytics(request, actor=user["username"])
        
        # Check for low-confidence results requiring approval
        from ..utils.database import AnalyticsResult
        low_confidence_results = db.query(AnalyticsResult).filter(
            AnalyticsResult.snapshot_id == results["snapshot_id"],
            AnalyticsResult.requires_review == True
        ).all()
        
        approval_requests = []
        for result in low_confidence_results:
            auto_approved, approval_request = policy_engine.evaluate_analytics_confidence(
                result, user["username"], user["role"]
            )
            if approval_request:
                approval_requests.append({
                    "request_id": approval_request.request_id,
                    "metric": result.metric_name,
                    "confidence": result.confidence_score,
                    "requires_approval": True
                })
        
        return {
            "success": True,
            "snapshot_id": results["snapshot_id"],
            "metrics": results["metrics"],
            "summary": results["summary"],
            "approval_requests": approval_requests
        }
        
    except Exception as e:
        api_logger.error(f"Failed to run analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/results")
async def get_analytics_results(
    snapshot_id: Optional[str] = None,
    client_id: Optional[int] = None,
    metric_type: Optional[str] = None,
    requires_review: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db_session),
    user: Dict = Depends(get_current_user)
):
    """Get analytics results with filters."""
    try:
        # Check permission
        policy_engine = PolicyEngine(db)
        allowed, reason = policy_engine.check_permission(user["role"], Permission.DATA_READ)
        if not allowed:
            raise HTTPException(status_code=403, detail=reason)
        
        from ..utils.database import AnalyticsResult
        query = db.query(AnalyticsResult)
        
        if snapshot_id:
            query = query.filter(AnalyticsResult.snapshot_id == snapshot_id)
        if client_id:
            query = query.filter(AnalyticsResult.client_id == client_id)
        if metric_type:
            query = query.filter(AnalyticsResult.metric_type == metric_type)
        if requires_review is not None:
            query = query.filter(AnalyticsResult.requires_review == requires_review)
        
        results = query.offset(skip).limit(limit).all()
        
        return [AnalyticsResultResponse.model_validate(r) for r in results]
        
    except Exception as e:
        api_logger.error(f"Failed to get analytics results: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Report generation endpoints
@app.post("/api/reports/generate", response_model=ReportResponse)
async def generate_report(
    request: ReportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
    user: Dict = Depends(get_current_user)
):
    """Generate a report."""
    try:
        # Check permission
        policy_engine = PolicyEngine(db)
        allowed, reason = policy_engine.check_permission(user["role"], Permission.REPORTS_GENERATE)
        if not allowed:
            raise HTTPException(status_code=403, detail=reason)
        
        # Generate report
        generator = ReportGenerator(db)
        report_path = generator.generate_report(
            report_type=request.report_type,
            format=request.format,
            client_ids=request.client_ids,
            start_date=request.start_date,
            end_date=request.end_date,
            include_audit_trail=request.include_audit_trail,
            include_explanations=request.include_explanations,
            actor=user["username"]
        )
        
        # Get file size
        file_size = report_path.stat().st_size
        
        return ReportResponse(
            report_id=report_path.stem,
            file_path=str(report_path),
            format=request.format,
            generated_at=datetime.utcnow(),
            generated_by=user["username"],
            record_count=0,  # Would be returned by generator in production
            file_size_bytes=file_size
        )
        
    except Exception as e:
        api_logger.error(f"Failed to generate report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/reports/{report_id}/download")
async def download_report(
    report_id: str,
    db: Session = Depends(get_db_session),
    user: Dict = Depends(get_current_user)
):
    """Download a generated report."""
    try:
        # Check permission
        policy_engine = PolicyEngine(db)
        allowed, reason = policy_engine.check_permission(user["role"], Permission.REPORTS_EXPORT)
        if not allowed:
            raise HTTPException(status_code=403, detail=reason)
        
        # Find report file
        reports_dir = Path(config.paths.reports)
        report_files = list(reports_dir.glob(f"{report_id}.*"))
        
        if not report_files:
            raise HTTPException(status_code=404, detail="Report not found")
        
        report_path = report_files[0]
        
        return FileResponse(
            path=str(report_path),
            filename=report_path.name,
            media_type="application/octet-stream"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Failed to download report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Governance endpoints
@app.get("/api/governance/permissions")
async def check_permissions(
    permission: str,
    resource: Optional[str] = None,
    db: Session = Depends(get_db_session),
    user: Dict = Depends(get_current_user)
):
    """Check if current user has a specific permission."""
    try:
        policy_engine = PolicyEngine(db)
        
        # Convert string to Permission enum
        try:
            perm = Permission(permission)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid permission: {permission}")
        
        allowed, reason = policy_engine.check_permission(user["role"], perm, resource)
        
        return {
            "permission": permission,
            "resource": resource,
            "allowed": allowed,
            "reason": reason,
            "user_role": user["role"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Failed to check permissions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/governance/approvals/pending")
async def get_pending_approvals(
    db: Session = Depends(get_db_session),
    user: Dict = Depends(get_current_user)
):
    """Get pending approval requests for current user."""
    try:
        policy_engine = PolicyEngine(db)
        pending = policy_engine.get_pending_approvals(user["role"])
        
        return [{
            "request_id": req.request_id,
            "request_type": req.request_type,
            "requester": req.requester,
            "action": req.action,
            "target": req.target,
            "confidence_score": req.confidence_score,
            "created_at": req.created_at.isoformat(),
            "expires_at": req.expires_at.isoformat(),
            "details": req.details
        } for req in pending]
        
    except Exception as e:
        api_logger.error(f"Failed to get pending approvals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/governance/approvals/{request_id}/process")
async def process_approval(
    request_id: str,
    decision: Dict[str, Any],
    db: Session = Depends(get_db_session),
    user: Dict = Depends(get_current_user)
):
    """Process an approval request."""
    try:
        policy_engine = PolicyEngine(db)
        
        approved = decision.get("approved", False)
        reason = decision.get("reason", None)
        
        success, message = policy_engine.process_approval(
            request_id=request_id,
            approver=user["username"],
            approver_role=user["role"],
            approved=approved,
            reason=reason
        )
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        return {
            "success": success,
            "message": message,
            "request_id": request_id,
            "approved": approved
        }
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Failed to process approval: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/governance/compliance/{framework}")
async def check_compliance(
    framework: str,
    db: Session = Depends(get_db_session),
    user: Dict = Depends(get_current_user)
):
    """Check compliance with specific framework."""
    try:
        # Check permission
        policy_engine = PolicyEngine(db)
        allowed, reason = policy_engine.check_permission(user["role"], Permission.AUDIT_READ)
        if not allowed:
            raise HTTPException(status_code=403, detail=reason)
        
        compliance_status = policy_engine.check_compliance(framework)
        
        return compliance_status
        
    except Exception as e:
        api_logger.error(f"Failed to check compliance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Audit log endpoints
@app.get("/api/audit/logs", response_model=List[Dict[str, Any]])
async def get_audit_logs(
    actor: Optional[str] = None,
    action: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db_session),
    user: Dict = Depends(get_current_user)
):
    """Get audit logs with filters."""
    try:
        # Check permission
        policy_engine = PolicyEngine(db)
        allowed, reason = policy_engine.check_permission(user["role"], Permission.AUDIT_READ)
        if not allowed:
            raise HTTPException(status_code=403, detail=reason)
        
        audit_trail = policy_engine.get_audit_trail(
            actor=actor,
            action=action,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        
        return audit_trail
        
    except Exception as e:
        api_logger.error(f"Failed to get audit logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Include AI Analytics router
try:
    from .ai_analytics import router as ai_analytics_router
    app.include_router(ai_analytics_router)
    api_logger.info("AI Analytics endpoints registered")
except ImportError as e:
    api_logger.warning(f"AI Analytics endpoints not available: {e}")

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    api_logger.info(f"Starting {config.app.name} v{config.app.version} with AI Analytics")
    
    # Initialize database
    db_manager = get_db_manager()
    api_logger.info("Database initialized")
    
    # Initialize AI Analytics components
    try:
        from .ai_analytics import initialize_ai_components, get_memory_manager
        api_logger.info("Initializing AI Analytics components...")
        ai_init_success = await initialize_ai_components()
        
        if ai_init_success:
            # Ensure approved model (tinyllama) is loaded
            memory_manager = get_memory_manager()
            if memory_manager:
                api_logger.info("Verifying approved model is loaded and ready...")
                approved_model_ready = await memory_manager.smart_model_load('tinyllama')
                
                if approved_model_ready:
                    api_logger.success("✅ AI System ready: Approved model 'tinyllama' loaded and operational")
                else:
                    api_logger.warning("⚠️ AI System partially ready: Components initialized but approved model failed to load")
            else:
                api_logger.success("AI Analytics components initialized successfully")
        else:
            api_logger.warning("AI Analytics components failed to initialize - continuing without AI")
    except Exception as e:
        api_logger.error(f"Error initializing AI components: {e}")
        api_logger.warning("Application will continue without AI Analytics features")
    
    # Validate policy
    from ..governance.policy_engine import PolicyValidator
    validator = PolicyValidator()
    valid, errors = validator.validate_policy()
    
    if not valid:
        api_logger.error(f"Policy validation failed: {errors}")
    else:
        api_logger.info("Policy validation passed")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    api_logger.info("Shutting down application with AI Analytics cleanup")
    
    # Cleanup AI components
    try:
        from .ai_analytics import enhanced_analytics
        if enhanced_analytics:
            await enhanced_analytics.cleanup()
            api_logger.info("AI Analytics cleanup completed")
    except Exception as e:
        api_logger.error(f"Error during AI cleanup: {e}")
    
    # Close database connections
    db_manager = get_db_manager()
    db_manager.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=config.api.host,
        port=config.api.port,
        reload=config.app.debug
    )
