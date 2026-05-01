#syntax=docker/dockerfile:1

# === Build stage: Install dependencies ===
FROM dhi.io/python:3.10-debian13-dev AS builder

WORKDIR /app

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# === Final stage: Runtime ===
FROM dhi.io/python:3.10-debian13

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Set PATH to use installed packages
ENV PATH=/root/.local/bin:$PATH

# Copy application code with proper ownership (DHI runtime images run as appuser)
COPY --chown=appuser:appuser backend . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()"

# Run application (appuser is the default user in DHI runtime images)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
