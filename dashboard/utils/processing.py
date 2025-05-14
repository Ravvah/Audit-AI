"""
Data processing utilities for the dashboard
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict, Any, List
import logging

logger = logging.getLogger("auditai.dashboard.data")

class DataProcessor:
    """
    Handles loading, filtering and processing metrics data for the dashboard.
    """
    
    def __init__(self, metrics_provider):
        """
        Initialize the data processor.
        
        Args:
            metrics_provider: Object that provides metrics data
        """
        self.metrics_provider = metrics_provider
        
    def load_and_filter_data(self, 
                           time_range: str, 
                           selected_model: Optional[str] = None) -> Tuple[pd.DataFrame, datetime, datetime]:
        """
        Load and filter data based on time range and model.
        
        Args:
            time_range: Time range filter ("Last 1 Hour", "Last 24 Hours", etc.)
            selected_model: Model name to filter by (None = all models)
            
        Returns:
            Tuple of (filtered dataframe, start time, end time)
        """
        # Calculate time range
        end_time = datetime.now()
        
        if time_range == "Last 1 Hour":
            start_time = end_time - timedelta(hours=1)
        elif time_range == "Last 24 Hours":
            start_time = end_time - timedelta(days=1)
        elif time_range == "Last 7 Days":
            start_time = end_time - timedelta(days=7)
        else:  # All Time
            start_time = datetime.min
        
        # Load raw data
        try:
            df = self.metrics_provider.get_metrics_dataframe()
        except Exception as e:
            logger.error(f"Error loading metrics data: {e}")
            return self.get_empty_dataframe(), start_time, end_time
        
        # Apply time filter
        if len(df) > 0 and 'timestamp' in df.columns:
            # Convert timestamp to datetime if it's a string
            if isinstance(df['timestamp'][0], str):
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                
            # Filter by time range
            if time_range != "All Time":
                df = df[(df['timestamp'] >= start_time) & (df['timestamp'] <= end_time)]
        
        # Apply model filter
        if selected_model and len(df) > 0 and 'model' in df.columns:
            df = df[df['model'] == selected_model]
        
        # Sort by timestamp
        if len(df) > 0 and 'timestamp' in df.columns:
            df = df.sort_values('timestamp')
            
        # Return processed data
        return df, start_time, end_time
    
    def get_empty_dataframe(self) -> pd.DataFrame:
        """
        Return an empty dataframe with the expected schema.
        
        Returns:
            pd.DataFrame: Empty dataframe with correct columns
        """
        return pd.DataFrame({
            'timestamp': [],
            'request_id': [],
            'model': [],
            'prompt_len': [],
            'completion_len': [],
            'hallucination_score': [],
            'fact_consistency': [],
            'drift_detected': [],
            'response_time_ms': [],
            'tokens_in': [],
            'tokens_out': [],
            'system_cpu_percent': [],
            'system_memory_bytes': [],
            'system_disk_percent': []
        })
    
    def calculate_additional_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate additional derived metrics.
        
        Args:
            df: Input dataframe with raw metrics
            
        Returns:
            pd.DataFrame: Enhanced dataframe with additional metrics
        """
        if len(df) == 0:
            return df
            
        # Make a copy to avoid warnings
        result = df.copy()
        
        # Add timestamp-based features
        if 'timestamp' in result.columns and len(result) > 0:
            if isinstance(result['timestamp'][0], str):
                result['timestamp'] = pd.to_datetime(result['timestamp'])
                
            result['hour'] = result['timestamp'].dt.hour
            result['day_of_week'] = result['timestamp'].dt.dayofweek
            
        # Calculate token efficiency (output/input ratio)
        if 'tokens_in' in result.columns and 'tokens_out' in result.columns:
            result['token_efficiency'] = result['tokens_out'] / result['tokens_in'].replace(0, 1)
            
        # Calculate response quality index
        if all(col in result.columns for col in ['hallucination_score', 'fact_consistency', 'response_time_ms']):
            # Normalize response time (lower is better)
            max_resp_time = result['response_time_ms'].max()
            if max_resp_time > 0:
                normalized_time = result['response_time_ms'] / max_resp_time
            else:
                normalized_time = 0
                
            # Quality index calculation (weighted average)
            result['response_quality_index'] = (
                0.4 * (1 - result['hallucination_score']) +  # Inverse of hallucination (higher is better)
                0.4 * result['fact_consistency'] +           # Factual consistency (higher is better)
                0.2 * (1 - normalized_time)                  # Inverse of normalized time (higher is better)
            )
            
        # Calculate hallucination severity
        if 'hallucination_score' in result.columns:
            # Categorize hallucination score
            result['hallucination_category'] = pd.cut(
                result['hallucination_score'],
                bins=[0, 0.3, 0.5, 1.0],
                labels=['Low', 'Medium', 'High']
            )
            
        return result
