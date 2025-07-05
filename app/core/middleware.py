"""
Authentication middleware for FastAPI.
"""
from typing import Callable, List

from fastapi import Request, Response, HTTPException, status
from fastapi.security import HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.security import verify_token


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle JWT authentication for protected routes.
    
    This middleware can be configured to:
    - Protect all routes by default
    - Allow specific routes to be public
    - Require authentication only for specific route patterns
    """
    
    def __init__(
        self,
        app,
        protected_paths: List[str] = None,
        public_paths: List[str] = None,
        require_auth_by_default: bool = False
    ):
        """
        Initialize the authentication middleware.
        
        Args:
            app: The FastAPI application
            protected_paths: List of path patterns that require authentication
            public_paths: List of path patterns that don't require authentication
            require_auth_by_default: If True, all routes require auth unless in public_paths
        """
        super().__init__(app)
        self.protected_paths = protected_paths or ["/api/v1/protected", "/api/v1/users"]
        self.public_paths = public_paths or [
            "/", "/docs", "/redoc", "/openapi.json", 
            "/auth/login", "/auth/register", "/auth/login/json",
            "/graphql"
        ]
        self.require_auth_by_default = require_auth_by_default
        self.security = HTTPBearer(auto_error=False)
    
    def _path_matches_patterns(self, path: str, patterns: List[str]) -> bool:
        """Check if path matches any of the given patterns."""
        for pattern in patterns:
            if path.startswith(pattern):
                return True
        return False
    
    def _requires_authentication(self, path: str) -> bool:
        """Determine if the given path requires authentication."""
        # Check if path is explicitly public
        if self._path_matches_patterns(path, self.public_paths):
            return False
        
        # Check if path is explicitly protected
        if self._path_matches_patterns(path, self.protected_paths):
            return True
        
        # Use default behavior
        return self.require_auth_by_default
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request through the authentication middleware."""
        
        # Skip authentication for non-protected paths
        if not self._requires_authentication(request.url.path):
            return await call_next(request)
        
        # Extract authorization header
        authorization = request.headers.get("Authorization")
        
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header missing",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Validate bearer token format
        try:
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                raise ValueError("Invalid scheme")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format. Expected: Bearer <token>",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify the JWT token
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            token_data = verify_token(token, credentials_exception)
            # Add user info to request state for use in route handlers
            request.state.current_user = {
                "username": token_data.username,
                "sub": token_data.sub
            }
        except HTTPException:
            raise credentials_exception
        
        # Continue to the actual route handler
        response = await call_next(request)
        return response


def create_auth_middleware(
    protected_paths: List[str] = None,
    public_paths: List[str] = None,
    require_auth_by_default: bool = False
) -> type:
    """
    Factory function to create configured authentication middleware.
    
    Args:
        protected_paths: List of path patterns that require authentication
        public_paths: List of path patterns that don't require authentication  
        require_auth_by_default: If True, all routes require auth unless in public_paths
        
    Returns:
        Configured AuthenticationMiddleware class
    """
    class ConfiguredAuthMiddleware(AuthenticationMiddleware):
        def __init__(self, app):
            super().__init__(
                app, 
                protected_paths, 
                public_paths, 
                require_auth_by_default
            )
    
    return ConfiguredAuthMiddleware
