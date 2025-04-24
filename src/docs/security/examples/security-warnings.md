# ⚠️ Security Warnings & Best Practices

This document highlights critical security considerations for developers using and contributing the **Revo Farmers** API. Follow these best practices to avoid vulnerabilities and ensure safe integration.

---

## 🔐 Token Handling
- **Do not store JWTs in localStorage**. Prefer secure, HTTP-only cookies or secure memory-based storage.
- **Always use HTTPS** to prevent token interception via man-in-the-middle (MITM) attacks.
- **Never share tokens** or expose them in client-side logs or URLs.

---

## 🧾 Authentication & Authorization
- Every request to a protected endpoint **must include** a valid `Authorization: Bearer <token>` header.
- JWTs are signed and verified using a secret defined in environment variables (`JWT_SECRET`). Ensure it remains private and unpredictable.
- Tokens expire after a configurable TTL (default: **1 hour**).
- There is **no refresh token** system at this stage — users must log in again after expiration.

---

## 🚧 API Usage Guidelines
- Avoid exposing **sensitive route structures** on the frontend (e.g., `/auth/profile`, `/escrow/release`).
- Enforce proper **input validation** and never trust client-side data blindly.
- Never hardcode secrets, private keys, or credentials in the frontend or public repos.

---

## 🛡️ Rate Limiting
- Rate limiting protects against brute force and abuse.
- Headers like `X-RateLimit-Remaining` and `Retry-After` should be monitored by clients.
- If your app repeatedly hits 429 errors, implement exponential backoff.

---

## 🚨 Error Handling
- Avoid exposing internal error messages or stack traces in production.
- Always sanitize error responses to prevent information leakage.

---

## 🔐 Security Configuration Location
Sensitive configuration is centralized in:
```
src/config/security.config.ts
```
Environment variables such as `JWT_SECRET`, `THROTTLE_TTL`, and `THROTTLE_LIMIT` should always be stored securely and never committed.

---

> Stay updated with [OWASP API Security Best Practices](https://owasp.org/www-project-api-security/) and apply secure coding habits in all contributions.

---

If you discover a vulnerability, **DO NOT** open a public issue. Please report it privately at [contact@nexacore.org](mailto:contact@nexacore.org).
