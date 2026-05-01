# Backend Dockerfile - FastAPI with Docker Hardened Images
# DHI images provide hardened, minimal base with security best practices
# Simplified approach: install dependencies in runtime stage

FROM dhi.io/python:3.10-debian13-dev

WORKDIR /app

# Install dependencies and postgresql-client
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Copy application
COPY backend .

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
    CMD python -m http.client localhost 8000 /health || exit 1

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
