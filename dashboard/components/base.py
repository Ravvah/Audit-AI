"""
Base component for dashboard UI
"""
import streamlit as st
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class DashboardComponent(ABC):
    """
    Abstract base class for all dashboard components.
    """
    
    def __init__(self, title: Optional[str] = None):
        """
        Initialize the dashboard component.
        
        Args:
            title: Optional component title
        """
        self.title = title
    
    @abstractmethod
    def render(self, **kwargs):
        """
        Render the component on the dashboard.
        
        Args:
            **kwargs: Additional parameters needed for rendering
        """
        pass
    
    def show_title(self):
        """
        Show the component title if available.
        """
        if self.title:
            st.markdown(f"<h2 class='section-header'>{self.title}</h2>", unsafe_allow_html=True)