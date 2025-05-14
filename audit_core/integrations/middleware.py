"""
FastAPI middleware for automatic auditing of inference requests
"""
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import json
from typing import Optional, Dict, Any, Callable

from audit_core.metrics.standard import StandardMetricsTracker
from audit_core.detection.hallucination import HallucinationDetector
from audit_core.detection.drift import DriftDetector

logger = logging.getLogger("audit_core.integrations")

class AuditMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for automatic auditing of inference requests.
    """
    
    def __init__(
        self, 
        app: ASGIApp,
        metrics_tracker: Optional[StandardMetricsTracker] = None,
        audit_path_filter: Optional[str] = None,
        extract_model_name: Optional[Callable[[Dict[str, Any]], str]] = None,
        extract_prompt: Optional[Callable[[Dict[str, Any]], str]] = None,
        extract_completion: Optional[Callable[[Dict[str, Any], Dict[str, Any]], str]] = None
    ):
        """
        Initialize the audit middleware.
        
        Args:
            app: FastAPI application
            metrics_tracker: Instance of metrics tracker (created if None)
            audit_path_filter: Path filter for auditing (None = all)
            extract_model_name: Function to extract model name from request
            extract_prompt: Function to extract prompt from request
            extract_completion: Function to extract completion from response
        """
        super().__init__(app)
        self.metrics_tracker = metrics_tracker or StandardMetricsTracker()
        self.audit_path_filter = audit_path_filter
        
        # Default extractors
        self.extract_model_name = extract_model_name or (lambda x: x.get("model", "default_model"))
        self.extract_prompt = extract_prompt or (lambda x: x.get("prompt", ""))
        self.extract_completion = extract_completion or (lambda req, resp: resp.get("response", resp.get("completion", "")))
        
        # Initialize detectors
        self.hallucination_detector = HallucinationDetector()
    
    def _should_audit_path(self, path: str) -> bool:
        """
        Determine if the path should be audited.
        
        Args:
            path: URL path to check
            
        Returns:
            True if path should be audited, False otherwise
        """
        # If no filter is set, audit all paths
        if not self.audit_path_filter:
            return True
            
        # Check if path matches the filter
        return self.audit_path_filter in path
    
    async def _log_audit_info(
        self, 
        request_body: Dict[str, Any], 
        response_body: bytes, 
        response_status: int,
        request_time: float
    ) -> None:
        """
        Log audit information for an API request.
        
        Args:
            request_body: The request body as a dictionary
            response_body: The response body as bytes
            response_status: HTTP status code
            request_time: Timestamp when request was received
        """
        # Skip if invalid or error responses
        if not response_body or response_status >= 400:
            logger.warning(f"Skipping audit for failed request with status {response_status}")
            return
            
        try:
            # Extract information
            model_name = self.extract_model_name(request_body)
            prompt = self.extract_prompt(request_body)
            
            # Parse response JSON
            response_json = {}
            try:
                response_json = json.loads(response_body)
            except Exception as e:
                logger.warning(f"Failed to parse response as JSON: {str(e)}")
                # Try to use as string if JSON parsing fails
                response_json = {"response": response_body.decode('utf-8', errors='replace')}
                
            # Extract completion text
            completion = self.extract_completion(request_body, response_json)
            
            # Calculate performance metrics
            response_time = (time.time() - request_time) * 1000  # convert to ms
            # token counts are determined by the StandardMetricsTracker's tokenizer
            
            # Calculate quality metrics
            hallucination_score = 0.0
            try:
                if prompt and completion:
                    hallucination_score = self.hallucination_detector.score_hallucination(
                        prompt=prompt, 
                        completion=completion
                    )
            except Exception as e:
                logger.warning(f"Hallucination detection failed: {str(e)}")
                
            # Record metrics (token counts computed inside tracker)
            self.metrics_tracker.log_inference(
                model=model_name,
                prompt=prompt,
                completion=completion,
                response_time_ms=int(response_time),
                status=response_status
            )
            logger.debug(f"Recorded audit metrics for request to model {model_name}")
            
        except Exception as e:
            logger.error(f"Error logging audit info: {str(e)}")
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process the request and response for audit logging."""
        # Initialize response_body to a default value
        response_body = b""
        response = None
        
        # Check if this is a path we should audit
        if not self._should_audit_path(str(request.url.path)):
            return await call_next(request)

        try:
            # Get request details
            request_time = time.time()
            request_body = await request.json() if request.method != "GET" else {}
            
            # Process the request through the application
            response = await call_next(request)
            
            # Only try to read response body if status code indicates success
            if 200 <= response.status_code < 300:
                # Get response content
                response_body = b""
                async for chunk in response.body_iterator:
                    response_body += chunk
                
                # We need to recreate the response as we've consumed the body iterator
                response = Response(
                    content=response_body,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type
                )
            
            # Log the audit info
            await self._log_audit_info(
                request_body=request_body,
                response_body=response_body,
                response_status=response.status_code,
                request_time=request_time
            )
            
            return response
            
        except Exception as e:
            # Log the error but don't block the response
            logging.error(f"Audit middleware error: {str(e)}")
            # Return the original response or a new one if we couldn't get that far
            if response:
                return response
            else:
                return await call_next(request)