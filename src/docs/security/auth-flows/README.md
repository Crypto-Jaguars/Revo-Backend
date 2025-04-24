# 🔐 Authentication Flow Documentation

This document explains the authentication mechanism used by the API of **Revo Farmers**.

## ✅ Overview

It uses **JSON Web Tokens (JWT)** for authentication. Users authenticate by sending their credentials to the `/auth/login` endpoint. If valid, the server responds with a JWT access token. This token must be included in all subsequent requests to protected routes.

---

## 📥 Login Flow

### 🔐 Request

**Endpoint:**
```http
POST /auth/login
```

**Request Headers:**
```http
Content-Type: application/json
```

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "securePassword123"
}
```

---

### 🔐 Backend Processing
1. Backend receives credentials and passes them to `authService.login()`
2. If credentials are valid, the backend signs a JWT containing `sub` (user ID) and `username`
3. JWT is returned along with user info

---

### 🔐 Successful Response
```json
{
  "user": {
    "id": 1,
    "username": "john_doe"
  },
  "accessToken": "<JWT_TOKEN>"
}
```

### 🔐 Error Response (Invalid Credentials)
```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
  "statusCode": 401,
  "message": "Invalid username or password",
  "error": "Unauthorized"
}
```

---

## 📤 Token Usage

Clients must send the JWT in the header for protected routes:
```http
GET /auth/profile
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Protected routes are guarded using NestJS `JwtAuthGuard`. If the token is missing, expired, or invalid:
- `401 Unauthorized` is returned.

---

## ⏳ Token Expiration

- Token expiration is configured at the `JwtModule` level (default assumed to be 1 hour unless overridden)
- There is **no refresh token** mechanism currently implemented.

---

## 📊 Diagram: Authentication Flows

The following diagrams facilitates a visual look on the authentication flow in the API.

### 🔐 Login Flow
![JWT Login Flow](./login-flow.png)

### 🔐 Authenticated Request Flow
![Authentication Request Flow](./auth-request-flow.png)

### 🔐 Logout Flow
![JWT Logout Flow](./logout-flow.png)

---
  
For more details, see: [OAuth 2.0](https://oauth.net/2/) | [OWASP API Security](https://owasp.org/www-project-api-security/) | [Swagger Auth](https://swagger.io/docs/specification/authentication/)
