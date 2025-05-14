"""
Base classes for metrics tracking
"""
import os
import json
import time
import logging
import threading
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
import pandas as pd
import numpy as np

class BaseMetricsTracker:
    """
    Abstract base class for metrics tracking.
    """
    def __init__(self, storage_path: str = "data/metrics"):
        """
        Initialize the metrics tracker.
        
        Args:
            storage_path: Path to store metrics data
        """
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        self.metrics = []
        self.logger = logging.getLogger("audit_core.metrics")
        self._lock = threading.Lock()
    
    def log_inference(self, **kwargs) -> Dict[str, Any]:
        """
        Log an inference with associated metrics.
        Abstract method to be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement log_inference")
    
    def get_metrics_dataframe(self) -> pd.DataFrame:
        """
        Return metrics as a DataFrame.
        May be overridden by subclasses to add preprocessing.
        """
        self._load_metrics()
        return pd.DataFrame(self.metrics)
    
    def _load_metrics(self) -> None:
        """Load metrics from disk."""
        self.metrics = []  # Reset to get fresh data
        metrics_file = os.path.join(self.storage_path, "metrics.jsonl")
        if os.path.exists(metrics_file):
            try:
                with open(metrics_file, 'r') as f:
                    for line in f:
                        if line.strip():
                            self.metrics.append(json.loads(line))
                self.logger.info(f"Loaded {len(self.metrics)} metrics from disk")
            except Exception as e:
                self.logger.error(f"Error loading metrics: {e}")
    
    def _write_to_disk(self, record: Dict[str, Any]) -> None:
        """Write metrics to disk in JSONL format."""
        metrics_file = os.path.join(self.storage_path, "metrics.jsonl")
        try:
            # Convert NumPy types to Python standard types
            serializable_record = {}
            for key, value in record.items():
                if isinstance(value, (np.integer, np.floating, np.bool_)):
                    serializable_record[key] = value.item()
                else:
                    serializable_record[key] = value
                    
            with self._lock, open(metrics_file, 'a') as f:
                f.write(json.dumps(serializable_record) + '\n')
        except Exception as e:
            self.logger.error(f"Error writing metrics to disk: {e}")
    
    def reset_metrics(self) -> bool:
        """
        Reset stored metrics.
        
        Returns:
            bool: True if reset was successful, False otherwise
        """
        metrics_file = os.path.join(self.storage_path, "metrics.jsonl")
        try:
            # Create backup
            if os.path.exists(metrics_file):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = f"{metrics_file}.bak.{timestamp}"
                import shutil
                shutil.copy2(metrics_file, backup_file)
            
            # Empty the file
            with open(metrics_file, 'w') as f:
                f.write("")
                
            self.metrics = []
            self.logger.info(f"Metrics reset successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error resetting metrics: {e}")
            return False