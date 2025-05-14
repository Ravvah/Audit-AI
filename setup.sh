#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# 1. Create a Python virtual environment named "auditai"
echo "🛠️  Creating virtual environment 'auditai'..."
python3 -m venv auditai

# 2. Activate the virtual environment
echo "🚀 Activating 'auditai'..."
# Supports bash, zsh, POSIX shells
source auditai/bin/activate

# 3. Upgrade pip and install UV if not already present
echo "📦  Upgrading pip and installing UV (if needed)..."
pip install --upgrade pip
if ! command -v uv &>/dev/null; then
  echo "⚡ Installing UV for fast dependency management..."
  pip install uv
fi

# 4. Install project dependencies via UV + pip interface
echo "📥  Installing dependencies from requirements.txt via UV..."
if [[ -f requirements.txt ]]; then
  uv pip install -r requirements.txt
else
  echo "⚠️  requirements.txt not found — creating a minimal template"
  cat <<EOF > requirements.txt
fastapi
uvicorn[standard]
requests
pydantic
deepchecks
pytest
EOF
  uv pip install -r requirements.txt
fi

echo "✅  Virtual environment 'auditai' is ready."
echo
echo "Next steps:"
echo "  1. Activate your venv:   source auditai/bin/activate"
echo "  2. Run the service:       make run"
