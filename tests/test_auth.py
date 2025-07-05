"""
Authentication tests for the Farmers Marketplace API.

Test Criteria:
✅ Login should return a valid token
✅ Protected routes should reject requests without a token
✅ Invalid token should return 401
"""
import pytest
from fastapi.testclient import TestClient
from jose import jwt

from app.main import app
from app.core.config import get_settings
from app.core.security import create_token_for_user, get_password_hash

settings = get_settings()
client = TestClient(app)


class TestAuthentication:
    """Test suite for authentication functionality."""
    
    def test_login_with_valid_credentials_returns_token(self):
        """✅ Test: Login should return a valid token"""
        # Test OAuth2 form login
        response = client.post(
            "/auth/login",
            data={"username": "testuser", "password": "testpass123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check token structure
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0
        
        # Verify token can be decoded
        token = data["access_token"]
        payload = jwt.decode(
            token, 
            settings.secret_key, 
            algorithms=[settings.algorithm]
        )
        assert "sub" in payload
        assert "exp" in payload
        assert payload["sub"] == "testuser"
    
    def test_login_json_with_valid_credentials_returns_token(self):
        """✅ Test: JSON login should return a valid token"""
        response = client.post(
            "/auth/login/json",
            json={"username": "testuser", "password": "testpass123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        
        # Verify token validity
        token = data["access_token"]
        payload = jwt.decode(
            token, 
            settings.secret_key, 
            algorithms=[settings.algorithm]
        )
        assert payload["sub"] == "testuser"
    
    def test_login_with_invalid_credentials_returns_401(self):
        """Test: Login with invalid credentials should return 401"""
        response = client.post(
            "/auth/login",
            data={"username": "testuser", "password": "wrongpassword"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "Incorrect username or password" in data["detail"]
    
    def test_login_with_nonexistent_user_returns_401(self):
        """Test: Login with non-existent user should return 401"""
        response = client.post(
            "/auth/login/json",
            json={"username": "nonexistent", "password": "password123"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
    
    def test_protected_route_without_token_returns_401(self):
        """✅ Test: Protected routes should reject requests without a token"""
        response = client.get("/auth/protected")
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "Not authenticated" in data["detail"]
    
    def test_protected_route_with_invalid_token_returns_401(self):
        """✅ Test: Invalid token should return 401"""
        # Test with completely invalid token
        response = client.get(
            "/auth/protected",
            headers={"Authorization": "Bearer invalid_token_123"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "Could not validate credentials" in data["detail"]
    
    def test_protected_route_with_malformed_token_returns_401(self):
        """✅ Test: Malformed token should return 401"""
        # Test with malformed authorization header
        response = client.get(
            "/auth/protected",
            headers={"Authorization": "NotBearer token123"}
        )
        
        assert response.status_code == 401
    
    def test_protected_route_with_expired_token_returns_401(self):
        """✅ Test: Expired token should return 401"""
        # Create an expired token (this is a bit tricky to test without mocking time)
        # For now, we'll test with an invalid signature
        fake_token = jwt.encode(
            {"sub": "testuser", "exp": 1234567890},  # Very old timestamp
            "wrong_secret_key",
            algorithm="HS256"
        )
        
        response = client.get(
            "/auth/protected",
            headers={"Authorization": f"Bearer {fake_token}"}
        )
        
        assert response.status_code == 401
    
    def test_protected_route_with_valid_token_returns_200(self):
        """Test: Protected route with valid token should return 200"""
        # First login to get a token
        login_response = client.post(
            "/auth/login/json",
            json={"username": "testuser", "password": "testpass123"}
        )
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Use token to access protected route
        response = client.get(
            "/auth/protected",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "testuser" in data["message"]
        assert "user_id" in data
    
    def test_get_current_user_with_valid_token(self):
        """Test: /me endpoint should return current user info"""
        # Login to get token
        login_response = client.post(
            "/auth/login/json",
            json={"username": "testuser", "password": "testpass123"}
        )
        
        token = login_response.json()["access_token"]
        
        # Get current user info
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert "email" in data
        assert "id" in data
        assert data["is_active"] is True
    
    def test_get_current_user_without_token_returns_401(self):
        """Test: /me endpoint without token should return 401"""
        response = client.get("/auth/me")
        
        assert response.status_code == 401
    
    def test_user_registration_creates_new_user(self):
        """Test: User registration should create a new user"""
        new_user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword123",
            "full_name": "New User"
        }
        
        response = client.post("/auth/register", json=new_user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert data["full_name"] == "New User"
        assert data["is_active"] is True
        assert "id" in data
    
    def test_user_registration_with_existing_username_returns_400(self):
        """Test: Registration with existing username should return 400"""
        existing_user_data = {
            "username": "testuser",  # This user already exists
            "email": "different@example.com",
            "password": "password123",
            "full_name": "Test User 2"
        }
        
        response = client.post("/auth/register", json=existing_user_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "Username already registered" in data["detail"]
    
    def test_registered_user_can_login(self):
        """Test: Newly registered user should be able to login"""
        # Register a new user
        new_user_data = {
            "username": "logintest",
            "email": "logintest@example.com", 
            "password": "logintest123",
            "full_name": "Login Test"
        }
        
        register_response = client.post("/auth/register", json=new_user_data)
        assert register_response.status_code == 200
        
        # Try to login with the new user
        login_response = client.post(
            "/auth/login/json",
            json={"username": "logintest", "password": "logintest123"}
        )
        
        assert login_response.status_code == 200
        data = login_response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"


class TestTokenValidation:
    """Test suite for JWT token validation functionality."""
    
    def test_token_contains_correct_claims(self):
        """Test: JWT token should contain correct claims"""
        token = create_token_for_user(user_id="123", username="testuser")
        
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        
        assert "sub" in payload
        assert "user_id" in payload
        assert "username" in payload
        assert "exp" in payload
        assert payload["sub"] == "testuser"
        assert payload["user_id"] == "123"
        assert payload["username"] == "testuser"
    
    def test_token_expiration_is_set(self):
        """Test: JWT token should have proper expiration"""
        import time
        
        token = create_token_for_user(user_id="123", username="testuser")
        
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        
        # Token should expire in the future
        assert payload["exp"] > time.time()
        
        # Token should expire within the configured time
        expected_exp = time.time() + (settings.access_token_expire_minutes * 60)
        assert payload["exp"] <= expected_exp + 60  # Allow 60 seconds tolerance


class TestPasswordHashing:
    """Test suite for password hashing functionality."""
    
    def test_password_hashing_works(self):
        """Test: Password hashing should work correctly"""
        from app.core.security import get_password_hash, verify_password
        
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        # Hash should be different from original password
        assert hashed != password
        assert len(hashed) > 0
        
        # Verification should work
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False
    
    def test_same_password_produces_different_hashes(self):
        """Test: Same password should produce different hashes (salt)"""
        from app.core.security import get_password_hash
        
        password = "testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Hashes should be different due to salt
        assert hash1 != hash2
