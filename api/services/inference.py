from abc import ABC, abstractmethod
import requests
from typing import Dict, Any, Optional, Tuple
from api.config import settings  # Use settings for base URL
import time  # Required for measuring response time

class InferenceService(ABC):
    """
    Abstract base class for inference services.
    """
    
    @abstractmethod
    def generate(self, 
                prompt: str, 
                model: str,
                max_tokens: Optional[int] = None,
                temperature: float = 0.7) -> Tuple[str, Dict[str, Any]]:
        """
        Generate a completion from a prompt.
        
        Args:
            prompt: Input text
            model: Model name
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Tuple[str, Dict[str, Any]]: (Generated text, metadata)
        """
        raise NotImplementedError("Subclasses must implement the generate method.")

class OllamaService(InferenceService):
    """
    Inference service using Ollama API.
    """
    
    def __init__(self, base_url: str = settings.OLLAMA_BASE_URL):
        """
        Initialize the Ollama service.
        
        Args:
            base_url: Base URL for Ollama API
        """
        self.base_url = base_url
        self.generate_endpoint = f"{base_url}/api/generate"
    
    def generate(self, 
                prompt: str, 
                model: str = "smollm2:360m", 
                max_tokens: Optional[int] = None,
                temperature: float = 0.7) -> Tuple[str, Dict[str, Any]]:
        """
        Generate a completion from a prompt using Ollama.
        
        Args:
            prompt: Input text
            model: Ollama model name
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Tuple[str, Dict[str, Any]]: (Generated text, metadata)
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "temperature": temperature
        }
        
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        
        start_time = time.time()
        response = requests.post(self.generate_endpoint, json=payload)
        response_time_ms = int((time.time() - start_time) * 1000)
        
        response.raise_for_status()
        result = response.json()
        
        completion = result.get("response", "")
        
        metadata = {
            "response_time_ms": response_time_ms,
            "model": model
        }
        
        if "prompt_eval_count" in result:
            metadata["tokens_in"] = result["prompt_eval_count"]
        if "eval_count" in result:
            metadata["tokens_out"] = result["eval_count"]
            
        return completion, metadata
