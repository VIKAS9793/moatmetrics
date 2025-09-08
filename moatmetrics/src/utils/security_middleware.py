"""
MoatMetrics Production Security Middleware
Implements production-grade security headers and protections
"""
import time
from typing import Dict, Optional
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import hashlib
import secrets


class SecurityMiddleware(BaseHTTPMiddleware):
    """Production security middleware with rate limiting and security headers"""
    
    def __init__(self, app, enable_rate_limiting: bool = True, rate_limit: int = 100):
        super().__init__(app)
        self.enable_rate_limiting = enable_rate_limiting
        self.rate_limit = rate_limit
        self.rate_limit_window = 60  # 1 minute window
        self.client_requests: Dict[str, list] = {}
        self.nonce_cache = set()
        
    async def dispatch(self, request: Request, call_next):
        """Process request with security checks"""
        
        # Generate request ID for tracking
        request_id = secrets.token_hex(8)
        request.state.request_id = request_id
        
        # Rate limiting
        if self.enable_rate_limiting:
            client_ip = self._get_client_ip(request)
            if self._is_rate_limited(client_ip):
                logger.warning(f"Rate limit exceeded for {client_ip}")
                return JSONResponse(
                    status_code=429,
                    content={
                        "status": "error",
                        "error": {
                            "code": "RATE_LIMIT_EXCEEDED",
                            "message": "Too many requests. Please try again later.",
                            "request_id": request_id
                        }
                    }
                )
        
        # Process request
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Add security headers
            response = self._add_security_headers(response, request)
            
            # Log request
            processing_time = time.time() - start_time
            logger.info(f"Request {request_id}: {request.method} {request.url.path} - "
                       f"{response.status_code} - {processing_time:.3f}s")
            
            return response
            
        except Exception as e:
            logger.error(f"Request {request_id} failed: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "error": {
                        "code": "INTERNAL_SERVER_ERROR",
                        "message": "An internal error occurred. Please try again later.",
                        "request_id": request_id
                    }
                }
            )
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address"""
        # Check for forwarded headers (for reverse proxies)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _is_rate_limited(self, client_ip: str) -> bool:
        """Check if client is rate limited"""
        current_time = time.time()
        
        # Initialize client tracking if not exists
        if client_ip not in self.client_requests:
            self.client_requests[client_ip] = []
        
        # Clean old requests outside the window
        self.client_requests[client_ip] = [
            req_time for req_time in self.client_requests[client_ip]
            if current_time - req_time < self.rate_limit_window
        ]
        
        # Check if rate limit exceeded
        if len(self.client_requests[client_ip]) >= self.rate_limit:
            return True
        
        # Add current request
        self.client_requests[client_ip].append(current_time)
        return False
    
    def _add_security_headers(self, response: Response, request: Request) -> Response:
        """Add production security headers"""
        
        # Generate nonce for CSP
        nonce = secrets.token_hex(16)
        
        security_headers = {
            # Prevent XSS attacks
            "X-XSS-Protection": "1; mode=block",
            
            # Prevent MIME type sniffing
            "X-Content-Type-Options": "nosniff",
            
            # Prevent clickjacking
            "X-Frame-Options": "DENY",
            
            # Referrer policy
            "Referrer-Policy": "strict-origin-when-cross-origin",
            
            # Content Security Policy
            "Content-Security-Policy": f"""
                default-src 'self';
                script-src 'self' 'nonce-{nonce}';
                style-src 'self' 'unsafe-inline';
                img-src 'self' data: https:;
                font-src 'self';
                connect-src 'self';
                frame-ancestors 'none';
                base-uri 'self';
                form-action 'self'
            """.replace('\\n', '').replace('  ', ' ').strip(),
            
            # HTTP Strict Transport Security (if HTTPS)
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            
            # Feature Policy / Permissions Policy
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            
            # Additional headers
            "X-Request-ID": request.state.request_id,
            "Cache-Control": "no-store, max-age=0",
            "Pragma": "no-cache"
        }
        
        # Add all security headers to response
        for header_name, header_value in security_headers.items():
            response.headers[header_name] = header_value
        
        return response


class InputValidationMiddleware(BaseHTTPMiddleware):
    """Validate and sanitize input data"""
    
    def __init__(self, app):
        super().__init__(app)
        self.max_request_size = 10 * 1024 * 1024  # 10MB
        self.blocked_patterns = [
            # SQL injection patterns
            r"(?i)(union|select|insert|update|delete|drop|create|alter|exec|execute)",
            # XSS patterns
            r"(?i)(<script|javascript:|on\w+\s*=)",
            # Command injection
            r"(?i)(;|\||&|`|\$\()"
        ]
    
    async def dispatch(self, request: Request, call_next):
        """Validate request before processing"""
        
        # Check request size
        if hasattr(request, '_body'):
            body_size = len(request._body)
            if body_size > self.max_request_size:
                return JSONResponse(
                    status_code=413,
                    content={
                        "status": "error",
                        "error": {
                            "code": "REQUEST_TOO_LARGE",
                            "message": "Request size exceeds maximum allowed limit."
                        }
                    }
                )
        
        # Validate headers
        user_agent = request.headers.get("User-Agent", "")
        if not user_agent or len(user_agent) > 500:
            logger.warning(f"Suspicious User-Agent: {user_agent[:100]}...")
        
        # Continue processing
        return await call_next(request)


def generate_security_token() -> str:
    """Generate cryptographically secure token"""
    return secrets.token_urlsafe(32)


def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """Hash password with salt using secure algorithm"""
    if salt is None:
        salt = secrets.token_hex(32)
    
    # Use PBKDF2 with SHA-256
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000  # iterations
    )
    
    return password_hash.hex(), salt


def verify_password(password: str, password_hash: str, salt: str) -> bool:
    """Verify password against hash"""
    computed_hash, _ = hash_password(password, salt)
    return secrets.compare_digest(computed_hash, password_hash)


# Security configuration
SECURITY_CONFIG = {
    "RATE_LIMITING": True,
    "RATE_LIMIT": 200,  # requests per minute
    "MAX_REQUEST_SIZE": 10 * 1024 * 1024,  # 10MB
    "JWT_EXPIRATION": 8 * 60 * 60,  # 8 hours
    "SECURE_HEADERS": True,
    "INPUT_VALIDATION": True
}
