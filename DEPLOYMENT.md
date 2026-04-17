# Deployment Information

## Public URL

**https://YOUR-APP.up.railway.app** *(fill in after deploying)*

## Platform

Railway (free $5 credit)

## Test Commands

### 1. Health Check (no auth required)

```bash
curl https://YOUR-APP.up.railway.app/health
```

**Expected response:**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "environment": "production",
  "uptime_seconds": 123.4,
  "total_requests": 42,
  "timestamp": "2026-04-17T10:00:00+00:00"
}
```

### 2. Root info

```bash
curl https://YOUR-APP.up.railway.app/
```

### 3. Ask Agent (requires API key)

```bash
curl -X POST https://YOUR-APP.up.railway.app/ask \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "question": "Hello"}'
```

**Expected:** 200 OK with agent response.

### 4. Test missing API key (should fail)

```bash
curl -X POST https://YOUR-APP.up.railway.app/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'
```

**Expected:** 401 Unauthorized.

### 5. Test rate limiting (should trigger 429 after 10 requests)

```bash
for i in {1..15}; do
  curl -s -o /dev/null -w "%{http_code}\n" \
    -X POST https://YOUR-APP.up.railway.app/ask \
    -H "X-API-Key: YOUR_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"question":"test"}'
done
```

**Expected:** First 10 return `200`, then `429`.

## Environment Variables Set

| Variable | Value |
|----------|-------|
| `AGENT_API_KEY` | (secret, generated with `openssl rand -hex 32`) |
| `ENVIRONMENT` | `production` |
| `APP_NAME` | `Production AI Agent` |
| `RATE_LIMIT_PER_MINUTE` | `10` |
| `DAILY_BUDGET_USD` | `10.0` |
| `PORT` | (auto-assigned by Railway) |

## Screenshots

See `screenshots/` folder:
- `dashboard.png` — Railway deployment dashboard
- `running.png` — Service running / health check OK
- `test.png` — Successful API test
- `rate_limit.png` — Rate limit triggered
