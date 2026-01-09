# CollectiveBrain V1 - Production Docker Image
# Multi-stage build for optimized size

# Stage 1: Build dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Production runtime
FROM python:3.11-slim

# Security: Create non-root user
RUN groupadd -r brain && useradd -r -g brain brain

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /home/brain/.local

# Copy application code
COPY --chown=brain:brain . .

# Set environment variables
ENV PATH=/home/brain/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user
USER brain

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from orchestrator import Orchestrator; Orchestrator()" || exit 1

# Default command
ENTRYPOINT ["python", "main.py"]
CMD ["status"]
