# 🔐 Authentication & Authorization Examples

**Revo Farmers**

The API uses a stateless authentication approach based on **JWT (JSON Web Tokens)**. Tokens are signed and verified using a secret stored in environment variables and are passed via the `Authorization: Bearer <token>` HTTP header. All protected routes are guarded using NestJS `JwtAuthGuard`, and expired or missing tokens result in `401 Unauthorized` responses.

⚠️ **Important Notes:**
- All tokens must be handled securely on the client side — do not store them in localStorage.
- Ensure HTTPS is used to avoid token interception.
- Refresh tokens are not currently implemented; access tokens must be renewed by logging in again.
- Rate limiting is applied across all routes to prevent abuse (see rate-limiting documentation).

Below are several request/response examples for common scenarios:

---

## ✅ Successful Login Response
```json
{
  "user": {
    "id": 42,
    "username": "farmer_jane",
    "email": "jane@example.com"
  },
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

## ✅ Authorized Request with Bearer Token
```http
GET /auth/profile HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## ❌ Unauthorized (Missing Token)
```http
GET /auth/profile HTTP/1.1
```
```json
{
  "statusCode": 401,
  "message": "Unauthorized",
  "error": "Unauthorized"
}
```

---

## ❌ Unauthorized (Invalid or Expired Token)
```http
GET /auth/profile HTTP/1.1
Authorization: Bearer invalid_token_here
```
```json
{
  "statusCode": 401,
  "message": "invalid token",
  "error": "Unauthorized"
}
```

---

## ❌ Accessing Protected Endpoint Without Auth
```http
GET /orders HTTP/1.1
```
```json
{
  "statusCode": 401,
  "message": "Unauthorized",
  "error": "Unauthorized"
}
```

---

## 🔁 Logout Request
```http
POST /auth/logout HTTP/1.1
Authorization: Bearer <JWT_TOKEN>
```
```json
{
  "message": "Logout successful"
}
```

---

## 🚫 Invalid Login Attempt
```http
POST /auth/login HTTP/1.1
Content-Type: application/json

{
  "username": "wrong_user",
  "password": "wrong_password"
}
```
```json
{
  "statusCode": 401,
  "message": "Invalid username or password",
  "error": "Unauthorized"
}
```

---

## 🛡️ Escrow API Access Examples

These endpoints relate to the core escrow functionality of Revolutionary Farmers and require proper authentication.

---

### ✅ Accessing Escrow Details
```http
GET /escrow/123 HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```
```json
{
  "escrowId": 123,
  "status": "pending",
  "buyerId": 42,
  "sellerId": 51,
  "amount": 100.00,
  "currency": "USDC"
}
```

---

### ✅ Releasing Escrow Funds
```http
POST /escrow/release HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "escrowId": 123
}
```
```json
{
  "message": "Funds released successfully",
  "transactionHash": "0xabc123..."
}
```

---

### ❌ Attempting Escrow Release Without Token
```http
POST /escrow/release HTTP/1.1
Content-Type: application/json

{
  "escrowId": 123
}
```
```json
{
  "statusCode": 401,
  "message": "Unauthorized",
  "error": "Unauthorized"
}
```

---

These examples help ensure secure implementation and consistent access to the API's authentication and escrow-related endpoints.
