"""
Governance and policy enforcement engine for MoatMetrics.

This module implements role-based access control, policy enforcement,
and human-in-the-loop decision making for low-confidence insights.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from pathlib import Path

from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from loguru import logger

from ..utils.database import (
    get_db_manager, AuditLog, ActionType, AnalyticsResult,
    ConfidenceLevel
)
from ..utils.config_loader import get_config, get_policy


class Permission(str, Enum):
    """System permissions enumeration."""
    DATA_READ = "data:read"
    DATA_WRITE = "data:write"
    DATA_DELETE = "data:delete"
    ANALYTICS_RUN = "analytics:run"
    ANALYTICS_CONFIGURE = "analytics:configure"
    REPORTS_GENERATE = "reports:generate"
    REPORTS_EXPORT = "reports:export"
    AUDIT_READ = "audit:read"
    AUDIT_EXPORT = "audit:export"
    GOVERNANCE_MODIFY = "governance:modify"
    USERS_MANAGE = "users:manage"
    ALL = "*"


class ApprovalStatus(str, Enum):
    """Approval workflow status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    AUTO_APPROVED = "auto_approved"


class ApprovalRequest(BaseModel):
    """Schema for approval requests."""
    request_id: str
    request_type: str
    requester: str
    requester_role: str
    action: str
    target: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    confidence_score: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    status: ApprovalStatus = ApprovalStatus.PENDING
    approver: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None


class PolicyEngine:
    """
    Main policy enforcement engine.
    
    Handles role-based access control, data governance policies,
    and human-in-the-loop approval workflows.
    """
    
    def __init__(self, db_session: Optional[Session] = None):
        """
        Initialize policy engine.
        
        Args:
            db_session: Optional database session
        """
        self.config = get_config()
        self.policy = get_policy()
        self.db_manager = get_db_manager()
        self.db_session = db_session or self.db_manager.get_session()
        self.logger = logger.bind(module="policy_engine")
        self.approval_queue: List[ApprovalRequest] = []
        
    def check_permission(
        self,
        user_role: str,
        permission: Permission,
        resource: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Check if a role has a specific permission.
        
        Args:
            user_role: Role of the user
            permission: Permission to check
            resource: Optional resource identifier
            
        Returns:
            Tuple of (allowed, reason)
        """
        self.logger.info(f"Checking permission {permission} for role {user_role}")
        
        # Get role permissions
        role_config = self.policy.get("roles", {}).get(user_role)
        
        if not role_config:
            return False, f"Role '{user_role}' not found in policy"
        
        role_permissions = role_config.get("permissions", [])
        
        # Check for wildcard permission
        if Permission.ALL.value in role_permissions:
            return True, "Role has full access"
        
        # Check specific permission
        if permission.value in role_permissions:
            return True, f"Role has {permission.value} permission"
        
        return False, f"Role lacks {permission.value} permission"
    
    def enforce_data_governance(
        self,
        action: str,
        data_type: str,
        file_size_mb: Optional[float] = None,
        file_type: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Enforce data governance policies.
        
        Args:
            action: Action being performed
            data_type: Type of data
            file_size_mb: File size in MB
            file_type: File extension
            
        Returns:
            Tuple of (allowed, reason)
        """
        governance = self.policy.get("data_governance", {})
        
        # Check file type
        if file_type:
            allowed_types = governance.get("allowed_file_types", [])
            if file_type.lower() not in allowed_types:
                return False, f"File type '{file_type}' not allowed. Allowed: {allowed_types}"
        
        # Check file size
        if file_size_mb:
            max_size = governance.get("max_file_size_mb", 100)
            if file_size_mb > max_size:
                return False, f"File size {file_size_mb}MB exceeds limit of {max_size}MB"
        
        # Check schema validation requirement
        if action == "upload" and governance.get("require_schema_validation", True):
            self.logger.info("Schema validation is required for uploads")
        
        return True, "Data governance check passed"
    
    def evaluate_analytics_confidence(
        self,
        result: AnalyticsResult,
        actor: str,
        actor_role: str
    ) -> Tuple[bool, Optional[ApprovalRequest]]:
        """
        Evaluate analytics result confidence and determine if review is needed.
        
        Args:
            result: Analytics result to evaluate
            actor: User who ran analytics
            actor_role: Role of the user
            
        Returns:
            Tuple of (auto_approved, approval_request)
        """
        analytics_gov = self.policy.get("analytics_governance", {})
        
        # Check confidence thresholds
        min_auto_confidence = analytics_gov.get("min_confidence_for_auto_action", 0.9)
        review_threshold = analytics_gov.get("require_human_review_below", 0.5)
        
        # Auto-approve high confidence
        if result.confidence_score >= min_auto_confidence:
            self.logger.info(f"Auto-approving result with confidence {result.confidence_score}")
            return True, None
        
        # Require review for low confidence
        if result.confidence_score < review_threshold or result.requires_review:
            self.logger.info(f"Human review required for confidence {result.confidence_score}")
            
            # Create approval request
            approval_request = ApprovalRequest(
                request_id=f"AR-{result.result_id}-{datetime.utcnow().timestamp()}",
                request_type="low_confidence_insight",
                requester=actor,
                requester_role=actor_role,
                action="approve_insight",
                target=f"analytics_result_{result.result_id}",
                details={
                    "metric_type": result.metric_type.value,
                    "metric_name": result.metric_name,
                    "value": result.value,
                    "confidence_score": result.confidence_score,
                    "explanation": result.explanation,
                    "recommendations": result.recommendations
                },
                confidence_score=result.confidence_score,
                expires_at=datetime.utcnow() + timedelta(
                    hours=self.policy.get("approval_workflows", {})
                    .get("low_confidence_insights", {})
                    .get("approval_timeout_hours", 12)
                )
            )
            
            self.approval_queue.append(approval_request)
            self._save_approval_request(approval_request)
            
            return False, approval_request
        
        # Medium confidence - log but auto-approve
        self.logger.info(f"Auto-approving medium confidence result: {result.confidence_score}")
        return True, None
    
    def request_approval(
        self,
        action: str,
        actor: str,
        actor_role: str,
        target: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> ApprovalRequest:
        """
        Create an approval request for sensitive actions.
        
        Args:
            action: Action requiring approval
            actor: User requesting action
            actor_role: Role of the user
            target: Target of the action
            details: Additional details
            
        Returns:
            ApprovalRequest object
        """
        workflows = self.policy.get("approval_workflows", {})
        
        # Determine workflow type
        if action == "data_deletion":
            workflow = workflows.get("data_deletion", {})
            request_type = "data_deletion"
        elif action == "policy_modification":
            workflow = workflows.get("policy_modification", {})
            request_type = "policy_modification"
        else:
            workflow = {"approval_timeout_hours": 24}
            request_type = "generic"
        
        # Create approval request
        approval_request = ApprovalRequest(
            request_id=f"AR-{request_type}-{datetime.utcnow().timestamp()}",
            request_type=request_type,
            requester=actor,
            requester_role=actor_role,
            action=action,
            target=target,
            details=details or {},
            expires_at=datetime.utcnow() + timedelta(
                hours=workflow.get("approval_timeout_hours", 24)
            )
        )
        
        self.approval_queue.append(approval_request)
        self._save_approval_request(approval_request)
        
        self.logger.info(f"Created approval request {approval_request.request_id}")
        
        return approval_request
    
    def process_approval(
        self,
        request_id: str,
        approver: str,
        approver_role: str,
        approved: bool,
        reason: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Process an approval request.
        
        Args:
            request_id: ID of the approval request
            approver: User processing the approval
            approver_role: Role of the approver
            approved: Whether to approve or reject
            reason: Optional reason for rejection
            
        Returns:
            Tuple of (success, message)
        """
        # Find request
        request = None
        for req in self.approval_queue:
            if req.request_id == request_id:
                request = req
                break
        
        if not request:
            return False, f"Approval request {request_id} not found"
        
        # Check if expired
        if datetime.utcnow() > request.expires_at:
            request.status = ApprovalStatus.EXPIRED
            return False, "Approval request has expired"
        
        # Check approver permissions
        workflows = self.policy.get("approval_workflows", {})
        workflow = workflows.get(request.request_type, {})
        allowed_roles = workflow.get("approver_roles", ["admin"])
        
        if approver_role not in allowed_roles:
            return False, f"Role {approver_role} cannot approve {request.request_type} requests"
        
        # Process approval
        request.approver = approver
        request.approved_at = datetime.utcnow()
        
        if approved:
            request.status = ApprovalStatus.APPROVED
            message = f"Request {request_id} approved by {approver}"
        else:
            request.status = ApprovalStatus.REJECTED
            request.rejection_reason = reason or "No reason provided"
            message = f"Request {request_id} rejected by {approver}: {reason}"
        
        # Log audit entry
        self._log_audit(
            actor=approver,
            actor_role=approver_role,
            action="approval_decision",
            target=request_id,
            success=True,
            details={
                "approved": approved,
                "request_type": request.request_type,
                "reason": reason
            }
        )
        
        self.logger.info(message)
        return True, message
    
    def get_pending_approvals(
        self,
        approver_role: Optional[str] = None
    ) -> List[ApprovalRequest]:
        """
        Get pending approval requests.
        
        Args:
            approver_role: Optional role filter
            
        Returns:
            List of pending approval requests
        """
        # Update expired requests
        current_time = datetime.utcnow()
        for request in self.approval_queue:
            if request.status == ApprovalStatus.PENDING and request.expires_at < current_time:
                request.status = ApprovalStatus.EXPIRED
        
        # Filter pending requests
        pending = [
            req for req in self.approval_queue
            if req.status == ApprovalStatus.PENDING
        ]
        
        # Filter by approver role if specified
        if approver_role:
            workflows = self.policy.get("approval_workflows", {})
            filtered = []
            
            for request in pending:
                workflow = workflows.get(request.request_type, {})
                allowed_roles = workflow.get("approver_roles", ["admin"])
                
                if approver_role in allowed_roles:
                    filtered.append(request)
            
            return filtered
        
        return pending
    
    def check_compliance(
        self,
        framework: str
    ) -> Dict[str, Any]:
        """
        Check compliance with specific framework.
        
        Args:
            framework: Compliance framework (GDPR, HIPAA, SOC2)
            
        Returns:
            Compliance status and requirements
        """
        compliance = self.policy.get("compliance", {})
        frameworks = compliance.get("frameworks", [])
        
        if framework not in frameworks:
            return {
                "compliant": False,
                "reason": f"Framework {framework} not configured"
            }
        
        # Check framework-specific requirements
        requirements = {
            "GDPR": {
                "data_residency": compliance.get("data_residency") == "on-premise",
                "encryption_at_rest": compliance.get("encryption_at_rest", False),
                "audit_logging": self.policy.get("audit_policy", {}).get("log_all_actions", False),
                "data_retention": self.policy.get("data_governance", {}).get("retention_days", 0) <= 365
            },
            "HIPAA": {
                "encryption_at_rest": compliance.get("encryption_at_rest", False),
                "audit_logging": self.policy.get("audit_policy", {}).get("log_all_actions", False),
                "access_control": bool(self.policy.get("roles"))
            },
            "SOC2": {
                "audit_logging": self.policy.get("audit_policy", {}).get("log_all_actions", False),
                "access_control": bool(self.policy.get("roles")),
                "data_retention": bool(self.policy.get("data_governance", {}).get("retention_days"))
            }
        }
        
        framework_reqs = requirements.get(framework, {})
        all_met = all(framework_reqs.values())
        
        return {
            "compliant": all_met,
            "framework": framework,
            "requirements": framework_reqs,
            "missing": [req for req, met in framework_reqs.items() if not met]
        }
    
    def enforce_retention_policy(
        self,
        data_type: str,
        created_date: datetime
    ) -> Tuple[bool, str]:
        """
        Enforce data retention policy.
        
        Args:
            data_type: Type of data
            created_date: When data was created
            
        Returns:
            Tuple of (should_retain, reason)
        """
        governance = self.policy.get("data_governance", {})
        retention_days = governance.get("retention_days", 365)
        
        age_days = (datetime.utcnow() - created_date).days
        
        if age_days > retention_days:
            return False, f"Data exceeds retention period of {retention_days} days"
        
        return True, f"Data within retention period ({age_days}/{retention_days} days)"
    
    def validate_algorithm_usage(
        self,
        algorithm: str
    ) -> Tuple[bool, str]:
        """
        Validate if an algorithm is allowed by policy.
        
        Args:
            algorithm: Algorithm name
            
        Returns:
            Tuple of (allowed, reason)
        """
        analytics_gov = self.policy.get("analytics_governance", {})
        allowed_algorithms = analytics_gov.get("allowed_algorithms", [])
        
        if algorithm.lower() in [a.lower() for a in allowed_algorithms]:
            return True, f"Algorithm {algorithm} is allowed"
        
        return False, f"Algorithm {algorithm} not in allowed list: {allowed_algorithms}"
    
    def get_audit_trail(
        self,
        actor: Optional[str] = None,
        action: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get audit trail with optional filters.
        
        Args:
            actor: Filter by actor
            action: Filter by action
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Maximum records to return
            
        Returns:
            List of audit entries
        """
        query = self.db_session.query(AuditLog)
        
        if actor:
            query = query.filter(AuditLog.actor == actor)
        if action:
            query = query.filter(AuditLog.action == action)
        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)
        
        query = query.order_by(AuditLog.timestamp.desc()).limit(limit)
        
        entries = query.all()
        
        return [{
            "entry_id": e.entry_id,
            "timestamp": e.timestamp.isoformat(),
            "actor": e.actor,
            "actor_role": e.actor_role,
            "action": e.action.value if hasattr(e.action, 'value') else e.action,
            "target": e.target,
            "success": e.success,
            "error_message": e.error_message,
            "details": e.details_json
        } for e in entries]
    
    def _save_approval_request(self, request: ApprovalRequest) -> None:
        """Save approval request to database."""
        # In production, save to a dedicated table
        # For now, log as audit entry
        self._log_audit(
            actor=request.requester,
            actor_role=request.requester_role,
            action="approval_request_created",
            target=request.request_id,
            success=True,
            details=request.model_dump(mode='json')
        )
    
    def _log_audit(
        self,
        actor: str,
        action: str,
        actor_role: Optional[str] = None,
        target: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log audit entry."""
        try:
            # Map string action to ActionType if possible
            try:
                action_type = ActionType[action.upper()]
            except (KeyError, AttributeError):
                # Use a generic action type or create audit entry with string
                action_type = action
            
            audit_entry = AuditLog(
                actor=actor,
                actor_role=actor_role,
                action=action_type if isinstance(action_type, ActionType) else action,
                target=target,
                target_type="governance",
                success=success,
                error_message=error_message,
                details_json=details or {}
            )
            
            self.db_session.add(audit_entry)
            self.db_session.commit()
            
        except Exception as e:
            self.logger.error(f"Failed to log audit entry: {e}")


class PolicyValidator:
    """
    Validates and tests policy configurations.
    """
    
    def __init__(self, policy_path: Optional[Path] = None):
        """
        Initialize policy validator.
        
        Args:
            policy_path: Optional path to policy file
        """
        self.policy_path = policy_path or Path("./config/policies/default_policy.json")
        self.logger = logger.bind(module="policy_validator")
    
    def validate_policy(self) -> Tuple[bool, List[str]]:
        """
        Validate policy configuration.
        
        Returns:
            Tuple of (valid, errors)
        """
        errors = []
        
        try:
            # Load policy
            with open(self.policy_path, "r") as f:
                policy = json.load(f)
            
            # Check required sections
            required_sections = ["version", "roles", "data_governance", "audit_policy"]
            for section in required_sections:
                if section not in policy:
                    errors.append(f"Missing required section: {section}")
            
            # Validate roles
            if "roles" in policy:
                for role_name, role_config in policy["roles"].items():
                    if "permissions" not in role_config:
                        errors.append(f"Role {role_name} missing permissions")
                    
                    # Check for at least one admin role
                    if not any("admin" in role.lower() for role in policy["roles"]):
                        errors.append("No admin role defined")
            
            # Validate data governance
            if "data_governance" in policy:
                gov = policy["data_governance"]
                
                if "retention_days" in gov and gov["retention_days"] < 0:
                    errors.append("Invalid retention_days value")
                
                if "max_file_size_mb" in gov and gov["max_file_size_mb"] <= 0:
                    errors.append("Invalid max_file_size_mb value")
            
            # Validate approval workflows
            if "approval_workflows" in policy:
                for workflow_name, workflow in policy["approval_workflows"].items():
                    if "approver_roles" not in workflow:
                        errors.append(f"Workflow {workflow_name} missing approver_roles")
                    
                    if "approval_timeout_hours" in workflow:
                        if workflow["approval_timeout_hours"] <= 0:
                            errors.append(f"Invalid timeout for workflow {workflow_name}")
            
            valid = len(errors) == 0
            
            if valid:
                self.logger.info("Policy validation passed")
            else:
                self.logger.error(f"Policy validation failed with {len(errors)} errors")
            
            return valid, errors
            
        except Exception as e:
            errors.append(f"Failed to load policy: {e}")
            return False, errors
    
    def test_permission(
        self,
        role: str,
        permission: str
    ) -> bool:
        """
        Test if a role has a specific permission.
        
        Args:
            role: Role to test
            permission: Permission to check
            
        Returns:
            True if permission granted
        """
        try:
            with open(self.policy_path, "r") as f:
                policy = json.load(f)
            
            role_config = policy.get("roles", {}).get(role, {})
            permissions = role_config.get("permissions", [])
            
            return permission in permissions or "*" in permissions
            
        except Exception as e:
            self.logger.error(f"Failed to test permission: {e}")
            return False
