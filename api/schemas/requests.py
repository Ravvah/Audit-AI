"""
Request schemas for the API
"""
from pydantic import BaseModel, Field
from typing import Optional

class InferenceRequest(BaseModel):
    """
    Model for inference request.
    """
    prompt: str = Field(..., description="Input text for the model", examples=["How are you ?"])
    model: str = Field("default", description="Model to use", examples=["smollm2:360m"])
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate", examples=[1024])
    temperature: Optional[float] = Field(0.7, description="Sampling temperature")
    
    class Config:
        schema_extra = {
            "example": {
                "prompt": "What is the capital of France?",
                "model": "smollm2:360m",
                "max_tokens": 100,
                "temperature": 0.7
            }
        }