# Unified Dockerfile for AuditAI - Supports both API and Dashboard services
FROM python:3.13-slim

# Install system dependencies for both API and visualizations
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    wget \
    cmake \
    pkg-config \
    libgoogle-perftools-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install UV via pip
RUN pip install --upgrade pip uv

# Create a UV-managed virtual environment
RUN uv venv && uv --version

# Set working directory
WORKDIR /app

# Copy requirements for better caching
COPY requirements.txt .

# Install all dependencies in one go
RUN uv pip install -r requirements.txt && uv cache prune

# Create data directories
RUN mkdir -p /app/data/metrics /app/data/drift

# Copy only the OOP implementation directories
COPY api/ /app/api/
COPY dashboard/ /app/dashboard/
COPY audit_core/ /app/audit_core/

COPY setup.py /app/
RUN pip install -e .

# Copy entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expose both API and dashboard ports
EXPOSE 8000 8501

# Set default service mode to API
ENV SERVICE_MODE=api

# Use entrypoint script to determine which service to run
ENTRYPOINT ["/app/entrypoint.sh"]