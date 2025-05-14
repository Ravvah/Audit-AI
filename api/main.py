"""
Main FastAPI application
"""
from fastapi import FastAPI
import uvicorn
from api.routers import inference
from api.config import settings
from audit_core.integrations.middleware import AuditMiddleware

app = FastAPI(
    title="AuditAI API",
    description="AI Observability API for LLM applications",
    version="1.0.0"
)

# Include routers
app.include_router(inference.router)

# Add audit middleware
app.add_middleware(
    AuditMiddleware,
    audit_path_filter="/v1/infer",
    extract_prompt=lambda x: x.get("prompt", ""),
    extract_model_name=lambda x: x.get("model", settings.DEFAULT_MODEL),
    extract_completion=lambda req, resp: resp.get("completion", "")
)

@app.get("/", tags=["health"])
async def health_check():
    """API health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=settings.PORT, reload=True)