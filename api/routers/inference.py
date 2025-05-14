"""
API endpoints for inference
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import Dict, Any

from audit_core.metrics.standard import StandardMetricsTracker
from audit_core.detection.hallucination import HallucinationDetector
from audit_core.detection.drift import DriftDetector

from api.schemas.requests import InferenceRequest
from api.schemas.responses import InferenceResponse
from api.services.inference import InferenceService, OllamaService

router = APIRouter(
    prefix="/v1",
    tags=["inference"]
)

hallucination_detector = HallucinationDetector()
drift_detector = DriftDetector()
metrics = StandardMetricsTracker()

def get_inference_service() -> InferenceService:
    """Dependency to get inference service."""
    return OllamaService()

@router.post("/infer", response_model=InferenceResponse)
async def infer(
    req: InferenceRequest, 
    background_tasks: BackgroundTasks,
    inference_service: InferenceService = Depends(get_inference_service)
):
    """
    Generate a completion from a prompt.
    """
    try:
        # Call inference service
        completion, service_metrics = inference_service.generate(
            prompt=req.prompt,
            model=req.model,
            max_tokens=req.max_tokens,
            temperature=req.temperature
        )
        
        # Calculate metrics
        hallucination_score = hallucination_detector.score_hallucination(req.prompt, completion)
        fact_consistency = hallucination_detector.get_fact_consistency(req.prompt, completion)
        
        # Calculate drift
        response_time_ms = service_metrics.get("response_time_ms", 0)
        tokens_out = service_metrics.get("tokens_out", len(completion.split()))
        drift_detected = drift_detector.detect_drift(
            hallucination_score=hallucination_score,
            response_time_ms=response_time_ms,
            token_count=tokens_out
        )
        
        # Record metrics in the background
        def record_metrics():
            metrics.log_inference(
                prompt=req.prompt,
                completion=completion,
                model=req.model,
                hallucination_score=hallucination_score,
                drift_detected=drift_detected,
                response_time_ms=response_time_ms,
                tokens_in=service_metrics.get("tokens_in", len(req.prompt.split())),
                tokens_out=tokens_out
            )
            
        background_tasks.add_task(record_metrics)
        
        # Prepare response
        metrics_response = {
            "hallucination_score": hallucination_score,
            "fact_consistency": fact_consistency,
            "response_time_ms": response_time_ms,
            "drift_detected": drift_detected
        }
        
        # Add token counts if available
        if "tokens_in" in service_metrics:
            metrics_response["tokens_in"] = service_metrics["tokens_in"]
        if "tokens_out" in service_metrics:
            metrics_response["tokens_out"] = service_metrics["tokens_out"]
        
        return InferenceResponse(
            completion=completion,
            model=req.model,
            prompt=req.prompt,
            metrics=metrics_response
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")