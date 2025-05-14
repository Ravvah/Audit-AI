"""
Chart component with enhanced hover functionality
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, List, Dict, Any

from .base import DashboardComponent

class Chart(DashboardComponent):
    """
    Chart component with enhanced tooltip/hover functionality.
    """
    
    def __init__(self, title: str = None, height: int = 400, description: str = None):
        """Initialize chart component"""
        super().__init__(title)
        self.height = height
        self.description = description
    
    def render_line_chart(self, 
                          data: pd.DataFrame, 
                          x: str, 
                          y: str, 
                          color: Optional[str] = None,
                          hover_data: Optional[List[str]] = None,
                          **kwargs):
        """
        Render a line chart with enhanced hover functionality.
        
        Args:
            data: DataFrame containing the data
            x: Column to use for x-axis
            y: Column to use for y-axis  
            color: Optional column to use for color
            hover_data: List of columns to show in hover tooltip
            **kwargs: Additional arguments to pass to plotly
        """
        if self.title:
            st.markdown(f"### {self.title}")
            
        if self.description:
            st.markdown(f"<div class='chart-description'>{self.description}</div>", 
                      unsafe_allow_html=True)
        
        # Add CSS class for chart container
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        if len(data) == 0:
            st.info(f"No data available for this chart.")
            st.markdown('</div>', unsafe_allow_html=True)
            return
            
        # Create plotly chart with enhanced hover
        fig = px.line(data, x=x, y=y, color=color, hover_data=hover_data, **kwargs)
        
        # Customize hover template
        hover_template = "<b>%{x}</b><br>%{y}<br>"
        if hover_data:
            for col in hover_data:
                if col != x and col != y:
                    hover_template += f"{col}: %{{customdata[{hover_data.index(col)}]}}<br>"
        
        fig.update_traces(
            hovertemplate=hover_template,
            hoverlabel=dict(
                bgcolor="rgba(50, 50, 77, 0.9)",
                font_size=12,
                font_color="white"
            )
        )
        
        # Set theme-compatible layout
        fig.update_layout(
            height=self.height,
            plot_bgcolor='rgba(30, 30, 47, 0.5)',
            paper_bgcolor='rgba(30, 30, 47, 0)',
            font_color='white',
            margin=dict(l=20, r=20, t=30, b=20),
            hovermode="closest",
            xaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(255,255,255,0.1)',
            ),
            yaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(255,255,255,0.1)',
            )
        )
        
        # Display the chart with config for better interactivity
        st.plotly_chart(fig, use_container_width=True, config={
            'displayModeBar': False,
            'responsive': True,
            'showTips': True,
        })
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    def render_scatter_chart(self, 
                            data: pd.DataFrame, 
                            x: str, 
                            y: str, 
                            color: Optional[str] = None,
                            size: Optional[str] = None,
                            hover_data: Optional[List[str]] = None,
                            **kwargs):
        """Render a scatter plot with enhanced hover functionality"""
        if self.title:
            st.markdown(f"### {self.title}")
            
        if self.description:
            st.markdown(f"<div class='chart-description'>{self.description}</div>", 
                      unsafe_allow_html=True)
        
        # Add CSS class for chart container
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        if len(data) == 0:
            st.info(f"No data available for this chart.")
            st.markdown('</div>', unsafe_allow_html=True)
            return
            
        # Create plotly scatter chart
        fig = px.scatter(data, x=x, y=y, color=color, size=size, hover_data=hover_data, **kwargs)
        
        # Set theme-compatible layout
        fig.update_layout(
            height=self.height,
            plot_bgcolor='rgba(30, 30, 47, 0.5)',
            paper_bgcolor='rgba(30, 30, 47, 0)',
            font_color='white',
            margin=dict(l=20, r=20, t=30, b=20),
            hovermode="closest"
        )
        
        # Display the chart with config for better interactivity
        st.plotly_chart(fig, use_container_width=True, config={
            'displayModeBar': False,
            'responsive': True,
        })
        
        st.markdown('</div>', unsafe_allow_html=True)