"""
Key metrics component for the AuditAI dashboard
"""
import streamlit as st
import pandas as pd
from .base import DashboardComponent
from typing import Dict, Any

class KeyMetricsComponent(DashboardComponent):
    """
    Component for displaying key performance indicators.
    """
    
    def __init__(self):
        """
        Initialize the key metrics component.
        """
        super().__init__(title="Key Performance Indicators")
    
    def render(self, df: pd.DataFrame, resource_stats: Dict[str, Any], **kwargs):
        """
        Render key metrics cards.
        
        Args:
            df: DataFrame with metrics data
            resource_stats: Resource usage statistics
        """
        self.show_title()
        
        # Data exists check
        data_exists = len(df) > 0
        
        # First row of metrics (4 cards)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Requests count
            self._render_requests_card(len(df))
            
        with col2:
            # Response time
            avg_resp_time = df['response_time_ms'].mean() if data_exists else 0
            self._render_response_time_card(avg_resp_time)
            
        with col3:
            # Hallucination score
            avg_hallu = df['hallucination_score'].mean() if data_exists else 0
            self._render_hallucination_card(avg_hallu)
            
        with col4:
            # Fact consistency
            avg_consistency = df['fact_consistency'].mean() if data_exists and 'fact_consistency' in df.columns else 0
            self._render_fact_consistency_card(avg_consistency)
            
        # Second row of metrics (3 cards)
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # CPU usage
            avg_cpu_time = resource_stats['avg_cpu_time_sec'] if resource_stats["count"] > 0 else 0
            self._render_cpu_card(avg_cpu_time)
            
        with col2:
            # Memory usage
            avg_memory = resource_stats['avg_memory_delta_mb'] if resource_stats["count"] > 0 else 0
            self._render_memory_card(avg_memory)
            
        with col3:
            # Token efficiency
            token_efficiency = df['token_efficiency'].mean() if data_exists and 'token_efficiency' in df.columns else 0
            self._render_token_efficiency_card(token_efficiency)
    
    def _render_requests_card(self, count: int):
        """Render requests count card."""
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon request-icon">📊</div>
            <div class="metric-content">
                <div class="metric-title">Requests Processed</div>
                <div class="metric-value">{count:,}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_response_time_card(self, avg_resp_time: float):
        """Render response time card."""
        resp_class = "positive-metric" if avg_resp_time < 1000 else "negative-metric" if avg_resp_time > 3000 else "neutral-metric"
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon response-icon">⏱️</div>
            <div class="metric-content">
                <div class="metric-title">Avg Response Time</div>
                <div class="metric-value {resp_class}">{avg_resp_time:.0f} ms</div>
                <div class="metric-trend {resp_class}">
                    {"Excellent" if avg_resp_time < 1000 else "Needs Attention" if avg_resp_time > 3000 else "Good"}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_hallucination_card(self, avg_hallu: float):
        """Render hallucination score card."""
        hallu_class = "negative-metric" if avg_hallu > 0.5 else "positive-metric" if avg_hallu < 0.3 else "neutral-metric"
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon hallucination-icon">🧠</div>
            <div class="metric-content">
                <div class="metric-title">Hallucination Score</div>
                <div class="metric-value {hallu_class}">{avg_hallu:.2f}</div>
                <div class="metric-trend {hallu_class}">
                    {"High Risk" if avg_hallu > 0.5 else "Low Risk" if avg_hallu < 0.3 else "Medium Risk"}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_fact_consistency_card(self, avg_consistency: float):
        """Render fact consistency card."""
        fact_class = "positive-metric" if avg_consistency > 0.7 else "negative-metric" if avg_consistency < 0.5 else "neutral-metric"
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon fact-icon">✓</div>
            <div class="metric-content">
                <div class="metric-title">Fact Consistency</div>
                <div class="metric-value {fact_class}">{avg_consistency:.2f}</div>
                <div class="metric-trend {fact_class}">
                    {("High" if avg_consistency > 0.7 else "Low" if avg_consistency < 0.5 else "Medium")}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_cpu_card(self, avg_cpu: float):
        """Render CPU usage card."""
        cpu_class = "negative-metric" if avg_cpu > 80 else "positive-metric" if avg_cpu < 40 else "neutral-metric"
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon cpu-icon">💻</div>
            <div class="metric-content">
                <div class="metric-title">CPU Usage</div>
                <div class="metric-value {cpu_class}">{avg_cpu:.1f}%</div>
                <div class="metric-progress-container">
                    <div class="metric-progress-bar" style="width: {min(100, avg_cpu)}%;"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_memory_card(self, avg_memory: float):
        """Render memory usage card."""
        memory_percent = min(100, (avg_memory / 8000) * 100)  # Assuming 8GB as reference
        memory_class = "negative-metric" if memory_percent > 80 else "positive-metric" if memory_percent < 40 else "neutral-metric"
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon memory-icon">🧠</div>
            <div class="metric-content">
                <div class="metric-title">Memory Usage</div>
                <div class="metric-value {memory_class}">{avg_memory:.1f} MB</div>
                <div class="metric-progress-container">
                    <div class="metric-progress-bar" style="width: {memory_percent}%;"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_token_efficiency_card(self, token_efficiency: float):
        """Render token efficiency card."""
        efficiency_class = "positive-metric" if token_efficiency > 1.5 else "negative-metric" if token_efficiency < 0.5 else "neutral-metric"
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon token-icon">🔄</div>
            <div class="metric-content">
                <div class="metric-title">Token Efficiency</div>
                <div class="metric-value {efficiency_class}">{token_efficiency:.2f}</div>
                <div class="metric-trend">Output/Input Ratio</div>
            </div>
        </div>
        """, unsafe_allow_html=True)