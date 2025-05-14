#!/bin/bash
# Determines which service to run based on SERVICE_MODE

# Exit immediately if a command exits with a non-zero status
set -e
export PYTHONPATH=/app:$PYTHONPATH
echo "Starting AuditAI in $SERVICE_MODE mode"

if [ "$SERVICE_MODE" = "api" ]; then
    echo "Starting API server on port 8000..."
    # Updated to use the new API path in OOP implementation
    exec uv run uvicorn api.main:app --host 0.0.0.0 --port 8000
elif [ "$SERVICE_MODE" = "dashboard" ]; then
    echo "Starting Dashboard on port 8501..."
    # Use the OOP implementation
    exec uv run streamlit run dashboard/main.py --server.port=8501 --server.address=0.0.0.0
else
    echo "Error: SERVICE_MODE must be 'api' or 'dashboard'"
    exit 1
fi