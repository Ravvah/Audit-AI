"""
Drift detection in LLM responses
"""
import numpy as np
from typing import Dict, Any, List, Union, Optional
import pandas as pd
import logging

logger = logging.getLogger("audit_core.drift")

class DriftDetector:
    """
    Detects drift in LLM responses.
    """
    
    def __init__(self, reference_data_path: Optional[str] = None, window_size: int = 10):
        """
        Initialize the drift detector.
        
        Args:
            reference_data_path: Optional path to reference data
            window_size: Size of the window for drift detection
        """
        self.window_size = window_size
        self.reference_stats = {}
        self.current_window = []
        
        # Load reference data if available
        if reference_data_path:
            self._load_reference_data(reference_data_path)
    
    def _load_reference_data(self, path: str):
        """
        Load reference statistics from a file.
        
        Args:
            path: Path to reference data file
        """
        try:
            self.reference_stats = pd.read_json(path).to_dict(orient="records")[0]
            logger.info(f"Reference data loaded: {self.reference_stats}")
        except Exception as e:
            logger.error(f"Error loading reference data: {e}")
            self.reference_stats = {}
    
    def detect_drift(self, 
                    hallucination_score: float, 
                    response_time_ms: int,
                    token_count: Optional[int] = None) -> bool:
        """
        Detect if current metrics show drift from reference.
        
        Args:
            hallucination_score: Hallucination score
            response_time_ms: Response time in milliseconds
            token_count: Token count (optional)
            
        Returns:
            bool: True if drift detected, False otherwise
        """
        # Record metrics in current window
        current_metrics = {
            "hallucination_score": hallucination_score,
            "response_time_ms": response_time_ms
        }
        
        if token_count is not None:
            current_metrics["token_count"] = token_count
            
        self.current_window.append(current_metrics)
        
        # Limit window size
        if len(self.current_window) > self.window_size:
            self.current_window.pop(0)
            
        # Not enough data or no reference, no drift
        if len(self.current_window) < self.window_size or not self.reference_stats:
            return False
            
        # Calculate statistics on current window
        window_df = pd.DataFrame(self.current_window)
        current_stats = {
            "hallucination_score_mean": window_df["hallucination_score"].mean(),
            "response_time_ms_mean": window_df["response_time_ms"].mean()
        }
        
        if "token_count" in window_df.columns:
            current_stats["token_count_mean"] = window_df["token_count"].mean()
            
        # Detect drift
        hallucination_drift = self._is_metric_drifting(
            current_stats.get("hallucination_score_mean", 0),
            self.reference_stats.get("hallucination_score_mean", 0),
            threshold=0.2
        )
        
        response_time_drift = self._is_metric_drifting(
            current_stats.get("response_time_ms_mean", 0),
            self.reference_stats.get("response_time_ms_mean", 0),
            threshold=0.5,
            is_time=True
        )
        
        # Consider drift if at least one metric drifts
        return hallucination_drift or response_time_drift
    
    def _is_metric_drifting(self, current_value: float, reference_value: float, 
                          threshold: float = 0.2, is_time: bool = False) -> bool:
        """
        Determine if a metric is drifting from its reference.
        
        Args:
            current_value: Current value
            reference_value: Reference value
            threshold: Relative detection threshold (percentage)
            is_time: Whether this is a time metric
            
        Returns:
            bool: True if metric is drifting, False otherwise
        """
        if reference_value == 0:
            return False
            
        # For time metrics, only consider drift for increases
        if is_time:
            relative_change = (current_value - reference_value) / reference_value
            return relative_change > threshold
        else:
            # For other metrics, consider drift in both directions
            relative_change = abs(current_value - reference_value) / reference_value
            return relative_change > threshold