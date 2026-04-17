# Production AI Agent — Day 12 Final Project

> **AICB-P1 · VinUniversity 2026**

Production-ready AI agent with Docker, security, and cloud deployment.

## ✅ Features

- **12-Factor App** — All config from environment variables
- **Docker** — Multi-stage build, non-root user, < 250MB image
- **Authentication** — API key required (X-API-Key header)
- **Rate Limiting** — 10 requests/minute per user
- **Cost Guard** — $10/day budget with auto-stop
- **Health Check** — `/health` liveness probe
- **Readiness Check** — `/ready` readiness probe
- **Graceful Shutdown** — Handles SIGTERM properly
- **Structured Logging** — JSON format for easy parsing
- **Input Validation** — Pydantic models
- **Security Headers** — X-Content-Type-Options, X-Frame-Options
- **CORS** — Configurable origins

## 🚀 Quick Start

### Run locally (Python)

```bash
pip install -r requirements.txt
export AGENT_API_KEY=my-secret-key
python -m uvicorn app.main:app --reload
```

### Run with Docker

```bash
docker build -t my-agent .
docker run -p 8000:8000 -e AGENT_API_KEY=my-secret-key my-agent
```

### Run with Docker Compose

```bash
docker compose up
```

## 🧪 Test Endpoints

```bash
# Health check (no auth)
curl http://localhost:8000/health

# Root info
curl http://localhost:8000/

# Ask agent (requires API key)
curl -X POST http://localhost:8000/ask \
  -H "X-API-Key: my-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello", "user_id": "test"}'

# Metrics (protected)
curl http://localhost:8000/metrics \
  -H "X-API-Key: my-secret-key"
```

## 🌐 Deploy to Railway

```bash
npm i -g @railway/cli
railway login
railway init
railway variables set AGENT_API_KEY=$(openssl rand -hex 32)
railway variables set ENVIRONMENT=production
railway up
railway domain
```

## 🌐 Deploy to Render

1. Push code to GitHub
2. Go to [render.com](https://render.com) → New → Blueprint
3. Connect your repo
4. Render reads `render.yaml` automatically
5. Deploy!

## 📁 Project Structure

```
my-production-agent/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   └── config.py        # Config from env vars
├── utils/
│   ├── __init__.py
│   └── mock_llm.py      # Mock LLM (no API key needed)
├── Dockerfile           # Multi-stage build
├── docker-compose.yml   # Local stack
├── railway.toml         # Railway config
├── render.yaml          # Render config
├── requirements.txt
├── .env.example         # Environment template
├── .dockerignore
├── .gitignore
└── README.md
```

## 🔒 Security Notes

- Never commit `.env` files (only `.env.example`)
- Rotate API keys regularly
- Use HTTPS in production (platforms handle this automatically)
- Set `ENVIRONMENT=production` to disable Swagger docs

## 📊 Response Codes

| Code | Meaning |
|------|---------|
| 200  | Success |
| 401  | Invalid/missing API key |
| 402  | Budget exceeded |
| 422  | Invalid input |
| 429  | Rate limit exceeded |
| 503  | Service not ready |
