"""
Resource metrics component for the AuditAI dashboard
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from .base import DashboardComponent
from typing import Dict, Any

class ResourceMetricsComponent(DashboardComponent):
    """
    Component for displaying resource utilization metrics.
    """
    
    def __init__(self):
        """
        Initialize the resource metrics component.
        """
        super().__init__(title="Resource Utilization")
    
    def render(self, df: pd.DataFrame, resource_stats: Dict[str, Any], **kwargs):
        """
        Render resource utilization visualizations.
        
        Args:
            df: DataFrame with metrics data
            resource_stats: Resource usage statistics
        """
        self.show_title()
        
        if len(df) == 0:
            st.info("No resource utilization data available yet.")
            return
            
        # Add a request sequence if it doesn't exist
        if 'request_seq' not in df.columns:
            df = df.copy()
            df['request_seq'] = np.arange(1, len(df) + 1)
            
        # Resource usage over requests
        resource_col1, resource_col2 = st.columns(2)
        
        with resource_col1:
            self._render_cpu_usage(df)
            
        with resource_col2:
            self._render_memory_usage(df)
            
        # Load progression chart - showing response time over requests
        self._render_response_time_curve(df)
        
        # Model comparison if multiple models
        if len(resource_stats["models"]) > 1:
            self._render_model_comparison(resource_stats)
    
    def _render_cpu_usage(self, df: pd.DataFrame):
        """
        Render CPU usage over requests.
        """
        # Use per-inference CPU time
        if 'cpu_time_sec' not in df.columns:
            st.info("CPU time data not available.")
            return

        st.subheader("CPU Time per Request")

        fig = px.line(
            df,
            x='request_seq',
            y='cpu_time_sec',
            labels={'request_seq': 'Request Count', 'cpu_time_sec': 'CPU Time (s)'},
        )

        # Optionally, could add thresholds for CPU time if needed

        # Customize layout
        fig.update_layout(
            height=350,
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_memory_usage(self, df: pd.DataFrame):
        """
        Render memory usage over requests.
        """
        # Use per-inference memory delta
        if 'memory_delta_bytes' not in df.columns:
            st.info("Memory delta data not available.")
            return
        
        st.subheader("Memory Delta per Request")

        # Convert bytes to MB for readability
        df['memory_delta_mb'] = df['memory_delta_bytes'] / (1024 * 1024)

        fig = px.line(
            df,
            x='request_seq',
            y='memory_delta_mb',
            labels={'request_seq': 'Request Count', 'memory_delta_mb': 'Memory Delta (MB)'},
        )

        # Customize layout
        fig.update_layout(
            height=350,
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_response_time_curve(self, df: pd.DataFrame):
        """
        Render response time load curve.
        
        Args:
            df: DataFrame with metrics data
        """
        st.subheader("Response Time Load Curve")
        
        # Add smoothed trend line using rolling average
        df_smooth = df.copy()
        if len(df) > 5:  # Only if we have enough data
            df_smooth['response_time_smooth'] = df['response_time_ms'].rolling(window=5, min_periods=1).mean()
        else:
            df_smooth['response_time_smooth'] = df['response_time_ms']
            
        # Create plot
        fig = px.line(
            df_smooth,
            x='request_seq',
            y=['response_time_ms', 'response_time_smooth'],
            labels={
                'request_seq': 'Request Count',
                'response_time_ms': 'Response Time (ms)',
                'response_time_smooth': 'Trend (5-pt avg)'
            },
            color_discrete_map={
                'response_time_ms': 'rgba(58, 123, 213, 0.4)',
                'response_time_smooth': '#00d2ff'
            }
        )
        
        # Customize layout
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            legend_title_text='',
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_model_comparison(self, resource_stats: Dict[str, Any]):
        """
        Render model comparison visualization.
        
        Args:
            resource_stats: Resource usage statistics
        """
        st.subheader("Model Resource Efficiency")
        
        # Create model comparison dataframe with updated CPU and memory metrics
        model_data = []
        for model_name, stats in resource_stats["models"].items():
            model_data.append({
                "Model": model_name,
                "Requests": stats["count"],
                "Avg CPU Time (s)": round(stats["avg_cpu_time_sec"], 3),
                "Avg Memory Delta (MB)": round(stats["avg_memory_delta_mb"], 1),
                "Avg Response Time (ms)": round(stats["avg_response_time_ms"], 0),
                "Avg Hallucination Score": round(stats["avg_hallucination_score"], 2),
            })
            
        model_df = pd.DataFrame(model_data)
        
        # Create comparison table with visual indicators
        self._render_model_comparison_table(model_df)
        
        # Resource Efficiency Visualization
        fig = px.scatter(
            model_df,
            x="Avg Response Time (ms)",
            y="Avg CPU Time (s)",
            size="Avg Memory Delta (MB)",
            color="Avg Hallucination Score",
            hover_name="Model",
            text="Model",
            labels={
                "Avg Response Time (ms)": "Response Time (ms)",
                "Avg CPU Time (s)": "CPU Time (s)"
            },
            color_continuous_scale='RdYlGn_r'
        )
        
        # Customize layout
        fig.update_layout(
            height=450,
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        
        # Improve text placement
        fig.update_traces(
            textposition='top center',
            marker=dict(sizemin=5)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_model_comparison_table(self, model_df: pd.DataFrame):
        """
        Render a custom HTML table for model comparison.

        Args:
            model_df: DataFrame with model comparison data
        """
        # Generate custom HTML table with visual indicators
        html_table = """
        <div class="model-comparison-table">
            <table>
                <thead>
                    <tr>
                        <th>Model</th>
                        <th>Requests</th>
                        <th>Response Time</th>
                        <th>CPU Usage</th>
                        <th>Memory</th>
                        <th>Hallucination</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for _, row in model_df.iterrows():
            response_time_width = min(100, (row["Avg Response Time (ms)"] / 5000) * 100)
            cpu_width = min(100, row["Avg CPU Time (s)"] * 20)  # Adjusted for new metric
            memory_width = min(100, (row["Avg Memory Delta (MB)"] / 4000) * 100)
            hallu_width = min(100, row["Avg Hallucination Score"] * 100)
            
            html_table += f"""
            <tr>
                <td class="model-name">{row["Model"]}</td>
                <td class="model-requests">{row["Requests"]}</td>
                <td>
                    <div class="bar-container">
                        <div class="bar-fill" style="width:{response_time_width}%"></div>
                        <span>{row["Avg Response Time (ms)"]:.0f} ms</span>
                    </div>
                </td>
                <td>
                    <div class="bar-container">
                        <div class="bar-fill" style="width:{cpu_width}%"></div>
                        <span>{row["Avg CPU Time (s)"]:.3f} s</span>
                    </div>
                </td>
                <td>
                    <div class="bar-container">
                        <div class="bar-fill" style="width:{memory_width}%"></div>
                        <span>{row["Avg Memory Delta (MB)"]:.0f} MB</span>
                    </div>
                </td>
                <td>
                    <div class="bar-container">
                        <div class="bar-fill hallu-bar" style="width:{hallu_width}%"></div>
                        <span>{row["Avg Hallucination Score"]:.2f}</span>
                    </div>
                </td>
            </tr>
            """
        
        html_table += """
                </tbody>
            </table>
        </div>
        """
        
        st.markdown(html_table, unsafe_allow_html=True)