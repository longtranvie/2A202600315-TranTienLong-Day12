# ============================================================
# Production Dockerfile - Simplified single-stage
# ============================================================
FROM python:3.11-slim

# Create non-root user
RUN groupadd -r agent && useradd -r -g agent -d /app agent

WORKDIR /app

# Install dependencies system-wide
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/
COPY utils/ ./utils/

RUN chown -R agent:agent /app

USER agent

ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
