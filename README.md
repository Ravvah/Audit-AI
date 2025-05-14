# AuditAI

**LLM Observability Platform for Ollama-based Inference**

AuditAI provides end-to-end observability for large language models (LLMs) running on Ollama. It audits model inferences, tracks performance and quality metrics, and detects drift and hallucinations in real time. The platform consists of:

- A FastAPI inference API (proxying to Ollama) that returns completions and structured observability data.
- A Streamlit dashboard for visualizing metrics, trends, and alerts.
- A back-end core (`audit_core`) for detection, logging, and metrics.
- Docker and Makefile support for local or containerized deployment.

---

## Architecture

AuditAI runs as three coordinated containers:

- **Ollama**: The LLM backend serving model completions.
- **API**: FastAPI service that proxies requests to Ollama, instruments all traffic, and emits metrics.
- **Dashboard**: Streamlit app for real-time visualization and analysis.

```
AuditAI/
├── api/            # FastAPI service and Pydantic schemas
├── audit_core/     # back-end for metrics, detection, middleware
├── dashboard/      # Streamlit app and style components
├── common/         # Shared utilities
├── setup.py        # Editable package install
├── Dockerfile.*    # Docker definitions for API and Dashboard
└── Makefile        # Build, run, and test targets
```

---

## Getting Started

1. **Clone the repository**
   ```powershell
   git clone https://github.com/<your-username>/Audit-AI.git
   cd Audit-AI
   ```
2. **Install Ollama** (if not already installed)
   - Follow instructions at https://docs.ollama.ai to install and start the Ollama engine on your machine.
3. **Pull the model**
   ```powershell
   make pull-model  # pulls the default model defined in the Makefile
   ```
4. **Launch services with Docker Compose** (recommended)
   ```powershell
   make build       # builds and starts Ollama, API, and Dashboard containers
   ```
5. **Access the UI and API**
   - Dashboard: http://localhost:8501
   - API:       http://localhost:8000

---

## Features

- **LLM Observability**: End-to-end tracing, latency, and token usage for every request.
- **Quality & Drift Detection**: Hallucination and drift scores per response.
- **Dashboard**: Visualize SLOs, trends, and anomalies interactively.
- **Load Testing**: Simulate parallel traffic to stress-test the stack.

---

## Deployment

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- `make` (optional)

### Containerized (Recommended)
1. Build and start all services:
   ```powershell
   make build
   ```
2. Access:
   - Dashboard: http://localhost:8501
   - API: http://localhost:8000
   - Ollama: http://localhost:11434 (default)
3. Stop and clean up:
   ```powershell
   make stop
   ```

### Local Development
1. Run the setup script:
   ```powershell
   .\setup.sh
   ```
2. Start API and Dashboard in separate terminals:
   ```powershell
   $Env:SERVICE_MODE = 'api'; bash .\entrypoint.sh
   $Env:SERVICE_MODE = 'dashboard'; bash .\entrypoint.sh
   ```

---

## Load Testing
- Load test (parallel requests):
  ```powershell
  make load-test         # default 100 requests
  make load-test NUM_REQUESTS=200  # custom number
  ```

---

## Metrics & Experimental Status

AuditAI’s metrics (latency, token counts, hallucination, drift, etc.) are experimental and designed for rapid iteration. See `METRICS.md` for details, limitations, and guidance on extending or tuning the observability stack for your production needs.

---

## License
MIT
