# 🚦 Rate Limiting Documentation

To protect the API from abuse and ensure stability, **rate limiting** is applied to incoming requests.

## ✅ General Policy

- **Limit**: 100 requests per 15 minutes per IP address *(configurable)*
- **TTL (Time-to-Live)**: 900 seconds (15 minutes)
- **Scope**: Applies globally to all routes

These values are configured in `security.config.ts` via NestJS ThrottlerModule and can be overridden using environment variables:

```env
THROTTLE_TTL=900
THROTTLE_LIMIT=100
```

---

## 📤 HTTP Response Headers
When rate limiting is enforced, responses will include the following headers:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 72
X-RateLimit-Reset: 1703456800
```

| Header                  | Description                                         |
|-------------------------|-----------------------------------------------------|
| `X-RateLimit-Limit`     | Max requests allowed in the time window             |
| `X-RateLimit-Remaining` | Requests remaining before rate limit is hit         |
| `X-RateLimit-Reset`     | Unix timestamp when limit resets                    |

---

## ❌ Exceeding the Limit
If the limit is exceeded, the API responds with:

```http
HTTP/1.1 429 Too Many Requests
{
  "statusCode": 429,
  "message": "Too many requests, please try again later."
}
```

---

## 🔐 Authenticated vs Public Routes
Currently, rate limits apply equally to public and authenticated users. Future versions may implement differentiated limits based on user role or endpoint sensitivity.

---

## 🛠️ Configuration Reference

Rate limiting is configured in:
```ts
// src/config/security.config.ts

export const getThrottlerConfig = (configService: ConfigService): ThrottlerModuleOptions => {
  return {
    ttl: configService.get<number>('THROTTLE_TTL') || 900, // 15 minutes
    limit: configService.get<number>('THROTTLE_LIMIT') || 100,
  };
};
```

Values can be set in `.env` or environment variables for flexibility.

---

For best practices, consider using exponential backoff and caching responses to reduce traffic load.
