"""
Quality metrics component for the AuditAI dashboard
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from .base import DashboardComponent

class QualityMetricsComponent(DashboardComponent):
    """
    Component for displaying quality-related metrics.
    """
    
    def __init__(self):
        """
        Initialize the quality metrics component.
        """
        super().__init__(title="Quality Metrics")
    
    def render(self, df: pd.DataFrame, **kwargs):
        """
        Render quality metrics visualizations.
        
        Args:
            df: DataFrame with metrics data
        """
        self.show_title()
        
        if len(df) == 0:
            st.info("No quality metrics data available. Generate some inferences to see metrics.")
            return
            
        # Create a two-column layout
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_hallucination_trend(df)
            
        with col2:
            self._render_quality_distribution(df)
            
        # Second row
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_fact_consistency_chart(df)
            
        with col2:
            self._render_hallucination_by_length(df)
    
    def _render_hallucination_trend(self, df: pd.DataFrame):
        """
        Render hallucination score trend over time.
        
        Args:
            df: DataFrame with metrics data
        """
        st.subheader("Hallucination Score Trend")
        
        # Add a request sequence if it doesn't exist
        if 'request_seq' not in df.columns:
            df = df.copy()
            df['request_seq'] = np.arange(1, len(df) + 1)
            
        # Create smoothed version for trendline
        df_smooth = df.copy()
        window_size = min(5, max(1, len(df) // 10))
        df_smooth['hallucination_smooth'] = df['hallucination_score'].rolling(window=window_size, min_periods=1).mean()
        
        # Create plot
        fig = px.line(
            df_smooth, 
            x='request_seq', 
            y=['hallucination_score', 'hallucination_smooth'],
            labels={
                'request_seq': 'Request Sequence',
                'hallucination_score': 'Hallucination Score',
                'hallucination_smooth': f'Trend ({window_size}-pt avg)'
            },
            color_discrete_map={
                'hallucination_score': 'rgba(255, 82, 82, 0.4)',
                'hallucination_smooth': 'rgba(255, 82, 82, 1.0)'
            }
        )
        
        # Add threshold lines
        fig.add_shape(
            type="line",
            y0=0.3, y1=0.3,
            x0=df['request_seq'].min(), x1=df['request_seq'].max(),
            line=dict(color="rgba(46, 204, 113, 0.7)", width=1, dash="dash")
        )
        fig.add_annotation(
            x=df['request_seq'].min(), 
            y=0.3,
            text="Low Risk",
            showarrow=False,
            yshift=10,
            font=dict(size=10, color="rgba(46, 204, 113, 1.0)")
        )
        
        fig.add_shape(
            type="line",
            y0=0.5, y1=0.5,
            x0=df['request_seq'].min(), x1=df['request_seq'].max(),
            line=dict(color="rgba(255, 82, 82, 0.7)", width=1, dash="dash")
        )
        fig.add_annotation(
            x=df['request_seq'].min(), 
            y=0.5,
            text="High Risk",
            showarrow=False,
            yshift=10,
            font=dict(size=10, color="rgba(255, 82, 82, 1.0)")
        )
        
        # Customize layout
        fig.update_layout(
            height=350,
            margin=dict(l=20, r=20, t=30, b=20),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            legend_title_text='',
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_quality_distribution(self, df: pd.DataFrame):
        """
        Render distribution of response quality index.
        
        Args:
            df: DataFrame with metrics data
        """
        st.subheader("Response Quality Distribution")
        
        if 'response_quality_index' not in df.columns:
            st.info("Response quality index not available.")
            return
            
        # Create histogram
        fig = px.histogram(
            df,
            x='response_quality_index',
            nbins=20,
            labels={'response_quality_index': 'Quality Index'},
            color_discrete_sequence=['rgba(58, 123, 213, 1.0)']
        )
        
        # Add vertical lines for quality thresholds
        fig.add_shape(
            type="line",
            y0=0, y1=df['response_quality_index'].value_counts().max(),
            x0=0.4, x1=0.4,
            line=dict(color="rgba(255, 177, 66, 0.7)", width=1, dash="dash")
        )
        fig.add_annotation(
            x=0.4, 
            y=0,
            text="Poor",
            showarrow=False,
            yshift=-15,
            font=dict(size=10, color="rgba(255, 177, 66, 1.0)")
        )
        
        fig.add_shape(
            type="line",
            y0=0, y1=df['response_quality_index'].value_counts().max(),
            x0=0.7, x1=0.7,
            line=dict(color="rgba(46, 204, 113, 0.7)", width=1, dash="dash")
        )
        fig.add_annotation(
            x=0.7, 
            y=0,
            text="Excellent",
            showarrow=False,
            yshift=-15,
            font=dict(size=10, color="rgba(46, 204, 113, 1.0)")
        )
        
        # Customize layout
        fig.update_layout(
            height=350,
            margin=dict(l=20, r=20, t=30, b=20),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            bargap=0.05
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_fact_consistency_chart(self, df: pd.DataFrame):
        """
        Render fact consistency visualization.
        
        Args:
            df: DataFrame with metrics data
        """
        st.subheader("Fact Consistency Analysis")
        
        if 'fact_consistency' not in df.columns:
            st.info("Fact consistency data not available.")
            return
            
        # Create a binned version for group analysis
        df_binned = df.copy()
        df_binned['consistency_bin'] = pd.cut(
            df_binned['fact_consistency'],
            bins=[0, 0.5, 0.7, 1.0],
            labels=['Low', 'Medium', 'High']
        )
        
        # Count records in each bin
        bin_counts = df_binned['consistency_bin'].value_counts().reset_index()
        bin_counts.columns = ['Consistency Level', 'Count']
        
        # Color map for consistency levels
        color_map = {
            'Low': 'rgba(255, 82, 82, 0.8)',
            'Medium': 'rgba(255, 177, 66, 0.8)',
            'High': 'rgba(46, 204, 113, 0.8)'
        }
        
        # Create bar chart
        fig = px.bar(
            bin_counts,
            x='Consistency Level',
            y='Count',
            color='Consistency Level',
            color_discrete_map=color_map,
            text='Count'
        )
        
        # Customize layout
        fig.update_layout(
            height=350,
            margin=dict(l=20, r=20, t=30, b=20),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            showlegend=False
        )
        
        # Display percentages on top of bars
        total = bin_counts['Count'].sum()
        for i, row in bin_counts.iterrows():
            percentage = row['Count'] / total * 100
            fig.add_annotation(
                x=row['Consistency Level'],
                y=row['Count'],
                text=f"{percentage:.1f}%",
                showarrow=False,
                yshift=15,
                font=dict(color="white", size=10)
            )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_hallucination_by_length(self, df: pd.DataFrame):
        """
        Render hallucination score by prompt/completion length.
        
        Args:
            df: DataFrame with metrics data
        """
        st.subheader("Hallucination vs. Text Length")
        
        # Create scatter plot
        fig = px.scatter(
            df,
            x='tokens_in',
            y='tokens_out',
            color='hallucination_score',
            labels={
                'tokens_in': 'Input Token Count',
                'tokens_out': 'Output Token Count',
                'hallucination_score': 'Hallucination Score'
            },
            color_continuous_scale='RdYlGn_r'
        )
        
        # Customize layout
        fig.update_layout(
            height=350,
            margin=dict(l=20, r=20, t=30, b=20),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        
        st.plotly_chart(fig, use_container_width=True)