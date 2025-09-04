"""
Agent orchestration module for MoatMetrics.

This module orchestrates automated pipelines for ETL, analytics,
and report generation with scheduling and retry capabilities.
"""

import time
import schedule
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path
from enum import Enum

from sqlalchemy.orm import Session
from loguru import logger

from ..utils.database import get_db_manager, ActionType, AuditLog
from ..utils.config_loader import get_config
from ..utils.schemas import AnalyticsRequest, FileUploadRequest
from ..etl.csv_processor import CSVProcessor
from ..analytics.engine import AnalyticsEngine
from ..governance.policy_engine import PolicyEngine
from .report_generator import ReportGenerator


class PipelineStatus(str, Enum):
    """Pipeline execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"


class MoatMetricsOrchestrator:
    """
    Orchestrates the complete MoatMetrics pipeline.
    
    Manages automated execution of ETL, analytics, and reporting
    with error handling, retries, and governance checks.
    """
    
    def __init__(self):
        """Initialize orchestrator."""
        self.config = get_config()
        self.db_manager = get_db_manager()
        self.logger = logger.bind(module="orchestrator")
        self.pipeline_status = PipelineStatus.PENDING
        self.retry_count = 0
        
    def run_complete_pipeline(
        self,
        data_files: Optional[Dict[str, Path]] = None,
        client_ids: Optional[List[int]] = None,
        generate_reports: bool = True,
        actor: str = "system"
    ) -> Dict[str, Any]:
        """
        Run the complete MoatMetrics pipeline.
        
        Args:
            data_files: Dictionary of data_type: file_path for ingestion
            client_ids: Optional list of client IDs to process
            generate_reports: Whether to generate reports at the end
            actor: User or system running the pipeline
            
        Returns:
            Pipeline execution results
        """
        self.logger.info("Starting MoatMetrics pipeline execution")
        self.pipeline_status = PipelineStatus.RUNNING
        
        results = {
            "pipeline_id": f"PIPE-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "started_at": datetime.utcnow().isoformat(),
            "steps": {},
            "status": None,
            "errors": []
        }
        
        db_session = self.db_manager.get_session()
        
        try:
            # Step 1: Data Ingestion (if files provided)
            if data_files:
                results["steps"]["ingestion"] = self._run_ingestion(
                    data_files, db_session, actor
                )
            
            # Step 2: Analytics
            results["steps"]["analytics"] = self._run_analytics(
                client_ids, db_session, actor
            )
            
            # Step 3: Governance Checks
            results["steps"]["governance"] = self._run_governance_checks(
                results["steps"].get("analytics", {}), db_session, actor
            )
            
            # Step 4: Report Generation
            if generate_reports:
                results["steps"]["reports"] = self._generate_reports(
                    client_ids, db_session, actor
                )
            
            # Pipeline completed successfully
            self.pipeline_status = PipelineStatus.COMPLETED
            results["status"] = "completed"
            results["completed_at"] = datetime.utcnow().isoformat()
            
            # Log success
            self._log_audit(
                db_session,
                actor=actor,
                action="PIPELINE_COMPLETE",
                target=results["pipeline_id"],
                success=True,
                details={"steps_completed": list(results["steps"].keys())}
            )
            
            self.logger.info(f"Pipeline {results['pipeline_id']} completed successfully")
            
        except Exception as e:
            self.pipeline_status = PipelineStatus.FAILED
            results["status"] = "failed"
            results["errors"].append(str(e))
            results["failed_at"] = datetime.utcnow().isoformat()
            
            self.logger.error(f"Pipeline failed: {e}")
            
            # Log failure
            self._log_audit(
                db_session,
                actor=actor,
                action="PIPELINE_FAILED",
                target=results["pipeline_id"],
                success=False,
                error_message=str(e),
                details=results
            )
            
            # Retry if configured
            if self.retry_count < self.config.agent.max_retries:
                self.retry_count += 1
                self.logger.info(f"Retrying pipeline (attempt {self.retry_count})")
                time.sleep(self.config.agent.retry_delay_seconds)
                return self.run_complete_pipeline(
                    data_files, client_ids, generate_reports, actor
                )
        
        finally:
            db_session.close()
        
        return results
    
    def _run_ingestion(
        self,
        data_files: Dict[str, Path],
        db_session: Session,
        actor: str
    ) -> Dict[str, Any]:
        """Run data ingestion step."""
        self.logger.info("Running data ingestion")
        
        ingestion_results = {
            "files_processed": 0,
            "records_processed": 0,
            "errors": []
        }
        
        processor = CSVProcessor(db_session)
        
        for data_type, file_path in data_files.items():
            try:
                result = processor.process_file(
                    file_path=file_path,
                    data_type=data_type,
                    validate_schema=True,
                    create_snapshot=True,
                    dry_run=False,
                    actor=actor
                )
                
                ingestion_results["files_processed"] += 1
                ingestion_results["records_processed"] += result.records_processed
                
                if not result.success:
                    ingestion_results["errors"].extend(result.validation_errors)
                
            except Exception as e:
                self.logger.error(f"Failed to process {data_type}: {e}")
                ingestion_results["errors"].append({
                    "file": str(file_path),
                    "error": str(e)
                })
        
        return ingestion_results
    
    def _run_analytics(
        self,
        client_ids: Optional[List[int]],
        db_session: Session,
        actor: str
    ) -> Dict[str, Any]:
        """Run analytics computations."""
        self.logger.info("Running analytics")
        
        engine = AnalyticsEngine(db_session)
        
        request = AnalyticsRequest(
            client_ids=client_ids,
            metric_types=["profitability", "license_efficiency", "resource_utilization", "spend_analysis"],
            include_explanations=True,
            confidence_threshold=self.config.analytics.confidence_threshold
        )
        
        results = engine.run_analytics(request, actor)
        
        return {
            "snapshot_id": results["snapshot_id"],
            "metrics_computed": len(results.get("summary", {}).get("total_metrics_computed", 0)),
            "requiring_review": results.get("summary", {}).get("metrics_requiring_review", 0),
            "average_confidence": results.get("summary", {}).get("average_confidence", 0)
        }
    
    def _run_governance_checks(
        self,
        analytics_results: Dict[str, Any],
        db_session: Session,
        actor: str
    ) -> Dict[str, Any]:
        """Run governance and compliance checks."""
        self.logger.info("Running governance checks")
        
        policy_engine = PolicyEngine(db_session)
        
        governance_results = {
            "compliance_checks": {},
            "pending_approvals": [],
            "policy_violations": []
        }
        
        # Check compliance with frameworks
        for framework in ["GDPR", "HIPAA", "SOC2"]:
            compliance = policy_engine.check_compliance(framework)
            governance_results["compliance_checks"][framework] = {
                "compliant": compliance["compliant"],
                "missing": compliance.get("missing", [])
            }
        
        # Get pending approvals
        pending = policy_engine.get_pending_approvals()
        governance_results["pending_approvals"] = [
            {
                "request_id": req.request_id,
                "type": req.request_type,
                "confidence": req.confidence_score
            }
            for req in pending
        ]
        
        # Check for low confidence metrics requiring review
        if analytics_results.get("requiring_review", 0) > 0:
            governance_results["policy_violations"].append({
                "type": "low_confidence_metrics",
                "count": analytics_results["requiring_review"],
                "action_required": "human_review"
            })
        
        return governance_results
    
    def _generate_reports(
        self,
        client_ids: Optional[List[int]],
        db_session: Session,
        actor: str
    ) -> Dict[str, Any]:
        """Generate reports."""
        self.logger.info("Generating reports")
        
        generator = ReportGenerator(db_session)
        
        report_results = {
            "reports_generated": [],
            "errors": []
        }
        
        # Generate different report types
        report_types = ["profitability", "licenses", "spend", "summary"]
        
        for report_type in report_types:
            try:
                report_path = generator.generate_report(
                    report_type=report_type,
                    format=self.config.reporting.default_format,
                    client_ids=client_ids,
                    include_audit_trail=self.config.reporting.include_audit_trail,
                    include_explanations=self.config.reporting.include_explanations,
                    actor=actor
                )
                
                report_results["reports_generated"].append({
                    "type": report_type,
                    "path": str(report_path),
                    "format": self.config.reporting.default_format
                })
                
            except Exception as e:
                self.logger.error(f"Failed to generate {report_type} report: {e}")
                report_results["errors"].append({
                    "type": report_type,
                    "error": str(e)
                })
        
        return report_results
    
    def schedule_pipeline(self) -> None:
        """
        Schedule pipeline execution based on configuration.
        
        Uses the schedule library to run pipeline at configured intervals.
        """
        if not self.config.agent.schedule_enabled:
            self.logger.info("Pipeline scheduling is disabled")
            return
        
        cron = self.config.agent.schedule_cron
        
        # Parse cron expression (simplified for prototype)
        # Format: "minute hour day month weekday"
        parts = cron.split()
        
        if len(parts) >= 2:
            hour = int(parts[1]) if parts[1] != "*" else 0
            minute = int(parts[0]) if parts[0] != "*" else 0
            
            # Schedule daily at specified time
            schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(
                self.run_complete_pipeline
            )
            
            self.logger.info(f"Pipeline scheduled to run daily at {hour:02d}:{minute:02d}")
        
        # Run scheduler
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def _log_audit(
        self,
        db_session: Session,
        actor: str,
        action: str,
        target: str,
        success: bool = True,
        error_message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log audit entry."""
        try:
            audit_entry = AuditLog(
                actor=actor,
                action=action,  # Will be mapped to ActionType if possible
                target=target,
                target_type="pipeline",
                success=success,
                error_message=error_message,
                details_json=details or {}
            )
            db_session.add(audit_entry)
            db_session.commit()
        except Exception as e:
            self.logger.error(f"Failed to log audit entry: {e}")


class DataValidator:
    """
    Validates data quality and consistency before processing.
    """
    
    def __init__(self):
        """Initialize data validator."""
        self.logger = logger.bind(module="data_validator")
    
    def validate_csv_structure(
        self,
        file_path: Path,
        expected_columns: List[str]
    ) -> Tuple[bool, List[str]]:
        """
        Validate CSV file structure.
        
        Args:
            file_path: Path to CSV file
            expected_columns: Expected column names
            
        Returns:
            Tuple of (valid, errors)
        """
        import pandas as pd
        
        errors = []
        
        try:
            df = pd.read_csv(file_path, nrows=1)
            actual_columns = set(df.columns)
            expected_columns = set(expected_columns)
            
            missing = expected_columns - actual_columns
            extra = actual_columns - expected_columns
            
            if missing:
                errors.append(f"Missing columns: {missing}")
            if extra:
                errors.append(f"Extra columns: {extra}")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"Failed to read CSV: {e}")
            return False, errors
    
    def validate_data_quality(
        self,
        file_path: Path
    ) -> Dict[str, Any]:
        """
        Validate data quality metrics.
        
        Args:
            file_path: Path to data file
            
        Returns:
            Quality metrics dictionary
        """
        import pandas as pd
        
        try:
            df = pd.read_csv(file_path)
            
            metrics = {
                "row_count": len(df),
                "column_count": len(df.columns),
                "missing_values": df.isnull().sum().sum(),
                "missing_percentage": (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100,
                "duplicate_rows": df.duplicated().sum(),
                "duplicate_percentage": (df.duplicated().sum() / len(df)) * 100
            }
            
            # Check for outliers in numeric columns
            numeric_cols = df.select_dtypes(include=['number']).columns
            outliers = 0
            
            for col in numeric_cols:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                outliers += ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum()
            
            metrics["outliers"] = outliers
            metrics["quality_score"] = max(0, 100 - metrics["missing_percentage"] - metrics["duplicate_percentage"])
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to validate data quality: {e}")
            return {"error": str(e)}


from typing import Tuple
