"""
Header component for the AuditAI dashboard
"""
import streamlit as st
from .base import DashboardComponent
from ..styles.base import DashboardStyles

class Header(DashboardComponent):
    """
    Header component for the dashboard.
    """
    
    def __init__(self, title: str = "LLM Observability Dashboard", subtitle: str = None):
        """
        Initialize the header component.
        
        Args:
            title: Dashboard title
            subtitle: Optional subtitle text
        """
        super().__init__()
        self.dashboard_title = title
        self.subtitle = subtitle or (
            "Monitor LLM performance, quality, and resource usage across requests. Track hallucinations, "
            "response quality, and system efficiency as request load increases."
        )
        self.styles = DashboardStyles()
    
    def setup_page(self):
        """
        Set up page configuration and apply CSS.
        """
        # Set page configuration
        st.set_page_config(
            page_title="AuditAI Dashboard",
            page_icon="🔍",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Apply CSS
        st.markdown(self.styles.get_css(), unsafe_allow_html=True)
    
    def render(self, **kwargs):
        """
        Render the header component.
        """
        st.markdown(f"<h1 class='header-title'>{self.dashboard_title}</h1>", unsafe_allow_html=True)
        st.markdown(self.subtitle)