"""
Response schemas for the API
"""
from pydantic import BaseModel, Field
from typing import Dict, Any

class InferenceResponse(BaseModel):
    """
    Model for inference response.
    """
    completion: str = Field(..., description="Generated text")
    model: str = Field(..., description="Model used")
    prompt: str = Field(..., description="Input text")
    metrics: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Response metrics"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "completion": "The capital of France is Paris.",
                "model": "smollm2:360m",
                "prompt": "What is the capital of France?",
                "metrics": {
                    "hallucination_score": 0.1,
                    "response_time_ms": 250,
                    "tokens_in": 7,
                    "tokens_out": 8
                }
            }
        }