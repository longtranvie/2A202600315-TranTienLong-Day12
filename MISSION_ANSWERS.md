# Day 12 Lab - Mission Answers

> **Student:** _____________________
> **Student ID:** _____________________
> **Date:** 17/4/2026

---

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found in `develop/app.py`

1. **Hardcoded API key** — Secret key written directly in source code; anyone reading the code can steal it. Secrets must come from environment variables.
2. **Hardcoded port (8000)** — Cloud platforms (Railway, Render, Cloud Run) dynamically assign the port via the `$PORT` environment variable. A hardcoded port will fail to bind in production.
3. **Debug mode enabled** — Exposes internal stack traces to users, leaking paths and implementation details. Also auto-reloads code, which is unsafe in production.
4. **No health check endpoint** — Platforms and load balancers need `/health` to know when to restart a crashed container or stop routing traffic.
5. **No graceful shutdown** — When the platform sends SIGTERM, the app dies immediately, interrupting in-flight requests and losing data.
6. **Uses `print()` instead of structured logging** — Log aggregators (Datadog, CloudWatch) need JSON to query/filter; plain print lines can't be indexed.
7. **No input validation** — Accepts any JSON payload, risking injection attacks or oversized requests that burn tokens.

### Exercise 1.3: Comparison table

| Feature | Develop | Production | Why Important? |
|---------|---------|------------|----------------|
| **Config** | Hardcoded values | `os.getenv()` | Same image runs in dev/staging/prod with different env vars |
| **Secrets** | In source code | Environment variables | Never commit secrets to Git |
| **Port** | Fixed `8000` | From `$PORT` env var | Cloud platforms assign port dynamically |
| **Health check** | None | `GET /health` | Platform restarts unhealthy containers |
| **Readiness** | None | `GET /ready` | Load balancer waits before routing traffic |
| **Logging** | `print()` | JSON structured | Can be parsed by log aggregators |
| **Shutdown** | Abrupt | Graceful (SIGTERM handler) | Finishes in-flight requests before exit |
| **Input validation** | None | Pydantic models | Rejects malformed/oversized input |
| **Error handling** | Crashes | HTTPException with proper codes | Clients get meaningful errors |

---

## Part 2: Docker

### Exercise 2.1: Dockerfile questions

1. **Base image:** `python:3.11-slim` — Official Python slim image (~130MB). Small, secure, has only essential packages.
2. **Working directory:** `/app` — All subsequent commands run from here. Standard convention for containerized apps.
3. **Why COPY requirements.txt first?** Docker caches layers. If requirements don't change, the `pip install` layer is reused on rebuild, saving minutes. If we copied source first, any code change would invalidate the pip install cache.
4. **CMD vs ENTRYPOINT:**
   - `CMD` = default command, can be overridden with `docker run image <other-command>`
   - `ENTRYPOINT` = fixed command, arguments passed via `docker run` become args to it
   - `CMD` is more flexible for general apps; `ENTRYPOINT` is for tools that always run the same binary

### Exercise 2.3: Image size comparison

| Version | Size | Difference |
|---------|------|------------|
| Develop (single-stage) | ~480 MB | baseline |
| Production (multi-stage) | ~220 MB | **~54% smaller** |

**Why smaller?** Multi-stage build drops the compiler (gcc), build tools, and pip cache. Only the installed Python packages + runtime are in the final image.

### Exercise 2.4: Docker Compose architecture

```
Client
  │
  ▼
┌─────────────┐
│    Nginx    │  (reverse proxy, port 80)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Agent    │  (FastAPI, port 8000)
└─────────────┘
```

Services communicate via Docker's internal network using service names as DNS (e.g., `http://agent:8000`).

---

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment

- **URL:** https://YOUR-APP.up.railway.app  *(fill in after deploy)*
- **Platform:** Railway
- **Environment variables set:** `AGENT_API_KEY`, `ENVIRONMENT=production`, `PORT` (auto)

### Exercise 3.2: `render.yaml` vs `railway.toml`

| Aspect | railway.toml | render.yaml |
|--------|--------------|-------------|
| **Format** | TOML | YAML |
| **Build spec** | `builder = "DOCKERFILE"` | `runtime: docker` |
| **Secret generation** | Manual via CLI | `generateValue: true` auto-generates |
| **Multi-service** | Separate file per service | Array of services in one file |
| **Deploy trigger** | Railway CLI or Git push | Git push only (Blueprints) |

---

## Part 4: API Security

### Exercise 4.1: API Key authentication — Test results

```bash
# Without key → 401
$ curl http://localhost:8000/ask -X POST -d '{"question":"Hi"}'
{"detail":"Invalid or missing API key. Include header: X-API-Key: <key>"}

# With key → 200
$ curl -H "X-API-Key: my-secret-key" http://localhost:8000/ask \
       -X POST -d '{"question":"Hi"}' -H "Content-Type: application/json"
{"question":"Hi","answer":"Hello! I'm a production AI agent...","model":"gpt-4o-mini","timestamp":"..."}
```

### Exercise 4.2: JWT flow (advanced)

JWT allows stateless auth across multiple servers:
1. User logs in with credentials → server returns signed JWT
2. Client sends JWT in `Authorization: Bearer <token>` header
3. Server verifies the signature (no DB lookup needed)
4. Tokens expire after a set time (e.g., 1 hour)

**Advantage over API keys:** Can carry user identity + roles without DB lookup. **Disadvantage:** Hard to revoke before expiry (need a blocklist).

### Exercise 4.3: Rate limiting

- **Algorithm used:** Sliding window (deque of timestamps for the last 60 seconds)
- **Limit:** 10 requests/minute per API key
- **Behavior:** Returns HTTP 429 with `Retry-After: 60` header when exceeded

Test result: First 10 requests return 200, requests 11-20 return 429.

### Exercise 4.4: Cost guard

Implementation tracks daily spending in memory (would use Redis for multi-instance):

```python
def check_and_record_cost(input_tokens, output_tokens):
    # Reset counter if new day
    if today != _cost_reset_day:
        _daily_cost = 0.0
    # Block if over budget
    if _daily_cost >= DAILY_BUDGET_USD:
        raise HTTPException(402, "Daily budget exhausted")
    # Estimate cost using gpt-4o-mini pricing
    cost = (input_tokens / 1000) * 0.00015 + (output_tokens / 1000) * 0.0006
    _daily_cost += cost
```

Returns HTTP 402 (Payment Required) when budget exhausted.

---

## Part 5: Scaling & Reliability

### Exercise 5.1: Health vs Readiness checks

**Difference:**
- **`/health`** — "Is the process alive?" Returns 200 if the server responds. Platform uses this to decide whether to RESTART the container.
- **`/ready`** — "Can I handle traffic?" Checks dependencies (DB, Redis). Load balancer uses this to decide whether to ROUTE traffic to this instance.

A container can be *healthy* but *not ready* (e.g., during startup while connecting to Redis).

### Exercise 5.2: Graceful shutdown

Registered a SIGTERM handler. On signal:
1. Mark `_is_ready = False` — load balancer stops sending new requests
2. Uvicorn finishes in-flight requests (timeout_graceful_shutdown=30s)
3. Close DB/Redis connections
4. Exit with code 0

Test: Sent long-running request + killed process with SIGTERM → request completed before exit.

### Exercise 5.3: Stateless design

**Stateful (bad):** Conversation history in `dict` in memory. Lost on restart, can't scale.

**Stateless (good):** Conversation history in Redis with key `history:{user_id}`. Any instance can serve any request. Survives restarts.

### Exercise 5.4: Load balancing

Ran `docker compose up --scale agent=3`. Nginx round-robins requests across 3 agents. Logs confirm different containers handled consecutive requests.

### Exercise 5.5: Stateless test

Created conversation on instance A → killed instance A → continued conversation on instance B. Conversation history preserved because state was in Redis, not instance memory.

---

## Summary

All production concepts implemented in `app/main.py`:

✅ 12-Factor config
✅ Multi-stage Dockerfile
✅ API key auth
✅ Rate limiting (10 req/min)
✅ Cost guard ($10/day)
✅ Health + readiness checks
✅ Graceful shutdown
✅ Structured JSON logging
✅ Input validation
✅ Security headers
✅ CORS
✅ Error handling
