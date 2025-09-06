"""
Simple Authentication and Authorization Module
Provides basic auth functions for API endpoints
"""
from typing import Dict, Any
from fastapi import HTTPException, Depends


def get_current_user() -> Dict[str, str]:
    """Get current user (simplified for prototype)."""
    return {"username": "admin", "role": "admin"}


def require_role(required_role: str):
    """Dependency factory for role-based access control"""
    def check_role(user: Dict[str, str] = Depends(get_current_user)) -> Dict[str, str]:
        if user["role"] != required_role and user["role"] != "admin":
            raise HTTPException(
                status_code=403, 
                detail=f"Access denied. {required_role} role required."
            )
        return user
    return check_role


def check_permission(user_role: str, required_permission: str) -> tuple[bool, str]:
    """Check if user role has required permission"""
    # Simple permission check - admin can do everything
    if user_role == "admin":
        return True, "Admin access granted"
    
    # Basic role-based permissions
    role_permissions = {
        "user": ["read", "query"],
        "analyst": ["read", "query", "analytics"],
        "admin": ["read", "write", "query", "analytics", "manage"]
    }
    
    user_perms = role_permissions.get(user_role, [])
    if required_permission in user_perms:
        return True, f"Permission {required_permission} granted"
    else:
        return False, f"Permission {required_permission} denied for role {user_role}"
