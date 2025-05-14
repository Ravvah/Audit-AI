"""
AuditAI Dashboard - LLM observability dashboard (OOP Implementation)
"""
import streamlit as st
import logging
import os
from datetime import datetime

from audit_core.metrics.standard import StandardMetricsTracker
from dashboard.components.header import Header
from dashboard.components.key_metrics import KeyMetricsComponent
from dashboard.components.quality_metrics import QualityMetricsComponent
from dashboard.components.resource_metrics import ResourceMetricsComponent
from dashboard.components.advanced_metrics import AdvancedMetricsComponent
from dashboard.utils.processing import DataProcessor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("auditai.dashboard")

class AuditAIDashboard:
    """
    Main dashboard application class using OOP components.
    """
    
    def __init__(self):
        """Initialize the dashboard application."""
        # Initialize metrics tracker
        self.metrics = StandardMetricsTracker()
        
        # Initialize components
        self.header = Header()
        self.key_metrics = KeyMetricsComponent()
        self.quality_metrics = QualityMetricsComponent()
        self.resource_metrics = ResourceMetricsComponent()
        self.advanced_metrics = AdvancedMetricsComponent()
        
        # Initialize data processor
        self.data_processor = DataProcessor(self.metrics)
        
    def reset_metrics_data(self):
        """Reset metrics data with multiple approaches and fallbacks"""
        try:
            # First try the direct method
            success = self.metrics.reset_metrics()
            if success:
                return True, "Metrics reset successfully!"
            
            # If that fails, try cleaning the storage path
            storage_path = self.metrics.storage_path
            metrics_file = os.path.join(storage_path, "metrics.jsonl")
            if os.path.exists(metrics_file):
                os.remove(metrics_file)
                self.metrics._load_metrics()  # Reload empty metrics
                return True, "Metrics reset by cleaning storage file!"
                
            return False, "No metrics data to reset."
            
        except Exception as e:
            logger.error(f"Error resetting metrics: {e}")
            return False, f"Error resetting metrics: {e}"
    
    def setup_sidebar(self):
        """Set up sidebar filters and controls."""
        # Sidebar filters
        st.sidebar.title("Filters")
        
        # Time range filter
        time_range = st.sidebar.selectbox(
            "Time Range",
            ["Last 1 Hour", "Last 24 Hours", "Last 7 Days", "All Time"],
            index=3
        )
        
        # Model filter (dynamic based on available data)
        df = self.metrics.get_metrics_dataframe()
        if len(df) > 0 and "model" in df.columns:
            available_models = ["All Models"] + sorted(df["model"].unique().tolist())
            selected_model = st.sidebar.selectbox("Model", available_models, index=0)
        else:
            available_models = ["All Models"]
            selected_model = "All Models"
        
        # Reset metrics button in sidebar
        st.sidebar.markdown("---")
        st.sidebar.subheader("Admin Controls")
        
        reset_col1, reset_col2 = st.sidebar.columns([3, 1])
        with reset_col2:
            if st.button("Reset", use_container_width=True):
                with st.spinner("Resetting metrics..."):
                    success, message = self.reset_metrics_data()
                    if success:
                        st.sidebar.success(message)
                    else:
                        st.sidebar.error(message)
        
        with reset_col1:
            st.markdown("Reset all metrics data")
            
        return time_range, selected_model
        
    def run(self):
        """Run the dashboard application."""
        # Set up page with header
        self.header.setup_page()
        
        # Render header
        self.header.render()
        
        # Set up sidebar and get filter values
        time_range, selected_model = self.setup_sidebar()
        
        # Load and filter data
        filtered_df, start_time, end_time = self.data_processor.load_and_filter_data(
            time_range, 
            selected_model if selected_model != "All Models" else None
        )
        
        # Get resource stats
        resource_stats = self.metrics.get_resource_usage_stats(
            model=selected_model if selected_model != "All Models" else None
        )
        
        # Calculate additional metrics
        filtered_df = self.data_processor.calculate_additional_metrics(filtered_df)
        
        # Main dashboard components
        self.key_metrics.render(filtered_df, resource_stats)
        
        # Create tabs for different metric categories
        tabs = st.tabs(["Quality Metrics", "Resource Usage", "Advanced Analysis"])
        
        with tabs[0]:
            self.quality_metrics.render(filtered_df)
        
        with tabs[1]:
            self.resource_metrics.render(filtered_df, resource_stats)
        
        with tabs[2]:
            self.advanced_metrics.render(filtered_df)

def main():
    """Main entry point for the dashboard."""
    dashboard = AuditAIDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()