"""
Standard implementation of metrics tracking
"""
import os
import time
import psutil
from datetime import datetime
from typing import Dict, Any, Optional
import pandas as pd

from audit_core.metrics.base import BaseMetricsTracker
from audit_core.detection.hallucination import HallucinationDetector
from audit_core.detection.drift import DriftDetector
from transformers import AutoTokenizer

# Initialize tokenizer for realistic token counting
_tokenizer = AutoTokenizer.from_pretrained("intfloat/multilingual-e5-base")

class StandardMetricsTracker(BaseMetricsTracker):
    """
    Standard implementation of metrics tracking with system monitoring.
    Implements the Singleton pattern.
    """
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(StandardMetricsTracker, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, 
                storage_path: str = "data/metrics",
                hallucination_detector: Optional[HallucinationDetector] = None,
                drift_detector: Optional[DriftDetector] = None):
        """
        Initialize the standard metrics tracker.
        
        Args:
            storage_path: Path to store metrics data
            hallucination_detector: Detector for hallucinations
            drift_detector: Detector for drift
        """
        # Avoid reinitializing the singleton
        if hasattr(self, "storage_path"):
            return
            
        super().__init__(storage_path)
        self.hallucination_detector = hallucination_detector or HallucinationDetector()
        self.drift_detector = drift_detector or DriftDetector()
        # Process handle for per-call resource deltas
        self.process = psutil.Process(os.getpid())
        
        # Load existing metrics
        self._load_metrics()
    
    def log_inference(self, 
                     prompt: str, 
                     completion: str, 
                     model: str,
                     response_time_ms: int,
                     tokens_in: Optional[int] = None,
                     tokens_out: Optional[int] = None,
                     status: str = "success") -> Dict[str, Any]:
        """
        Log an inference with associated metrics.
        
        Args:
            prompt: Input text
            completion: Generated response
            model: Model name
            response_time_ms: Response time in milliseconds
            tokens_in: Input token count
            tokens_out: Output token count
            status: Request status
            
        Returns:
            Dict[str, Any]: Recorded metrics
        """
        # Record process-level resource snapshot before inference
        start_cpu = self.process.cpu_times()
        start_mem = self.process.memory_info().rss
        
        # 2. Calculate hallucination score
        hallucination_score = self.hallucination_detector.score_hallucination(prompt, completion)
        
        # 3. Check for drift
        drift_detected = self.drift_detector.detect_drift(
            hallucination_score=hallucination_score,
            response_time_ms=response_time_ms,
            token_count=tokens_out
        )
        
        # 4. Create metrics record
        timestamp = datetime.now().isoformat()
        
        # Token-based length using tokenizer if not provided
        in_tokens = tokens_in if tokens_in is not None else len(_tokenizer.encode(prompt, add_special_tokens=False))
        out_tokens = tokens_out if tokens_out is not None else len(_tokenizer.encode(completion, add_special_tokens=False))
        record = {
            "request_id": f"req_{int(time.time() * 1000)}",
            "timestamp": timestamp,
            "model": model,
            "tokens_in": in_tokens,
            "tokens_out": out_tokens,
            "hallucination_score": hallucination_score,
            "drift_detected": drift_detected,
            "response_time_ms": response_time_ms,
            "status": status
        }
        
        # 5. Calculate fact consistency if appropriate
        if hallucination_score < 0.8:  # Only calculate for potentially relevant responses
            fact_consistency = self.hallucination_detector.get_fact_consistency(prompt, completion)
            record["fact_consistency"] = fact_consistency
        
        # 6. Write to disk
        # Capture post-inference resource usage
        end_cpu = self.process.cpu_times()
        end_mem = self.process.memory_info().rss
        # CPU time spent (user + system) in seconds
        record["cpu_time_sec"] = (end_cpu.user + end_cpu.system) - (start_cpu.user + start_cpu.system)
        # Additional memory allocated (bytes)
        record["memory_delta_bytes"] = end_mem - start_mem
        # Optionally capture disk usage
        try:
            record["disk_percent"] = psutil.disk_usage("/").percent
        except Exception:
            record["disk_percent"] = None
        self._write_to_disk(record)
        
        return record
    
    def get_resource_usage_stats(self, model: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate resource usage statistics.
        
        Args:
            model: Model to filter by (None = all models)
            
        Returns:
            Dict[str, Any]: Resource usage statistics
        """
        df = self.get_metrics_dataframe()
        # Fill missing resource delta columns for legacy records
        if 'cpu_time_sec' not in df.columns:
            df['cpu_time_sec'] = 0.0
        if 'memory_delta_bytes' not in df.columns:
            df['memory_delta_bytes'] = 0.0

        if len(df) == 0:
            return {
                "count": 0,
                "avg_cpu_time_sec": 0,
                "avg_memory_delta_mb": 0,
                "avg_response_time_ms": 0,
                "models": {}
            }
        
        # Filter by model if specified
        if model:
            df_filtered = df[df['model'] == model]
        else:
            df_filtered = df
        
        # Calculate global statistics
        result = {
            "count": len(df_filtered),
            "avg_cpu_time_sec": float(df_filtered['cpu_time_sec'].mean()),
            "avg_memory_delta_mb": float(df_filtered['memory_delta_bytes'].mean() / 1024 / 1024),
            "avg_response_time_ms": float(df_filtered['response_time_ms'].mean()),
            "models": {}
        }
        
        # Calculate per-model statistics
        models = df['model'].unique()
        for model_name in models:
            model_df = df[df['model'] == model_name]
            result["models"][model_name] = {
                "count": len(model_df),
                "avg_cpu_time_sec": float(model_df['cpu_time_sec'].mean()),
                "avg_memory_delta_mb": float(model_df['memory_delta_bytes'].mean() / 1024 / 1024),
                "avg_response_time_ms": float(model_df['response_time_ms'].mean()),
                "avg_hallucination_score": float(model_df['hallucination_score'].mean())
            }
            
        return result