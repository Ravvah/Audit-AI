"""
Advanced metrics component for the AuditAI dashboard
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from sklearn.decomposition import PCA
from .base import DashboardComponent

class AdvancedMetricsComponent(DashboardComponent):
    """
    Component for displaying advanced analytics and metrics.
    """
    
    def __init__(self):
        """
        Initialize the advanced metrics component.
        """
        super().__init__(title="Advanced Metrics & Analytics")
    
    def render(self, df: pd.DataFrame, **kwargs):
        """
        Render advanced metrics visualizations.
        
        Args:
            df: DataFrame with metrics data
        """
        self.show_title()
        
        if len(df) < 5:
            st.info("Not enough data for advanced analytics. Need at least 5 data points.")
            return
            
        # Create a two-column layout
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_correlation_heatmap(df)
            
        with col2:
            self._render_drift_analysis(df)
            
        # Second row
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_token_efficiency_analysis(df)
            
        with col2:
            self._render_dimensionality_reduction(df)
    
    def _render_correlation_heatmap(self, df: pd.DataFrame):
        """
        Render correlation heatmap between metrics.
        
        Args:
            df: DataFrame with metrics data
        """
        st.subheader("Metrics Correlation")
        
        # Select numeric columns for correlation
        numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
        
        # Filter relevant metrics
        relevant_metrics = [
            'hallucination_score', 'fact_consistency', 'response_time_ms', 
            'tokens_in', 'tokens_out', 'system_cpu_percent', 'system_memory_bytes'
        ]
        
        # Keep only metrics that exist in the data
        metrics_to_use = [col for col in relevant_metrics if col in numeric_cols]
        
        if len(metrics_to_use) < 2:
            st.info("Not enough metrics for correlation analysis.")
            return
            
        # Calculate correlation matrix
        corr_matrix = df[metrics_to_use].corr()
        
        # Create heatmap
        fig = px.imshow(
            corr_matrix,
            text_auto='.2f',
            color_continuous_scale='RdBu_r',
            labels=dict(x="Metric", y="Metric", color="Correlation"),
            x=corr_matrix.columns,
            y=corr_matrix.index
        )
        
        # Customize layout
        fig.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add interpretation
        self._add_correlation_interpretation(corr_matrix)
    
    def _add_correlation_interpretation(self, corr_matrix: pd.DataFrame):
        """
        Add interpretation of key correlations.
        
        Args:
            corr_matrix: Correlation matrix
        """
        # Find strongest correlations (excluding self-correlations)
        strongest = []
        for col in corr_matrix.columns:
            for idx in corr_matrix.index:
                if col != idx:  # Avoid self-correlation
                    corr = corr_matrix.loc[idx, col]
                    if abs(corr) > 0.3:  # Only consider meaningful correlations
                        strongest.append({
                            'metric1': col,
                            'metric2': idx,
                            'correlation': corr,
                            'abs_corr': abs(corr)
                        })
        
        # Sort by absolute correlation strength
        if strongest:
            strongest = sorted(strongest, key=lambda x: x['abs_corr'], reverse=True)
            
            # Show top 3 correlations
            with st.expander("Correlation Insights"):
                for i, item in enumerate(strongest[:3]):
                    direction = "positive" if item['correlation'] > 0 else "negative"
                    strength = "strong" if abs(item['correlation']) > 0.7 else "moderate" if abs(item['correlation']) > 0.5 else "weak"
                    
                    st.markdown(
                        f"**{i+1}. {item['metric1']}** has a {strength} {direction} correlation "
                        f"({item['correlation']:.2f}) with **{item['metric2']}**."
                    )
    
    def _render_drift_analysis(self, df: pd.DataFrame):
        """
        Render drift analysis visualization.
        
        Args:
            df: DataFrame with metrics data
        """
        st.subheader("Drift Detection Analysis")
        
        if 'drift_detected' not in df.columns:
            st.info("Drift detection data not available.")
            return
            
        # Check if we have any drift detected
        if df['drift_detected'].sum() == 0:
            st.markdown("No drift has been detected in the data.")
            return
            
        # Add a request sequence if it doesn't exist
        if 'request_seq' not in df.columns:
            df = df.copy()
            df['request_seq'] = np.arange(1, len(df) + 1)
            
        # Create plot showing when drift was detected
        fig = px.scatter(
            df,
            x='request_seq',
            y='hallucination_score',
            color='drift_detected',
            labels={
                'request_seq': 'Request Sequence',
                'hallucination_score': 'Hallucination Score',
                'drift_detected': 'Drift Detected'
            },
            color_discrete_map={
                True: 'red',
                False: 'rgba(58, 123, 213, 0.7)'
            }
        )
        
        # Connect the dots with a line
        fig.add_trace(
            px.line(
                df,
                x='request_seq',
                y='hallucination_score'
            ).data[0]
        )
        
        # Customize layout
        fig.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add drift statistics
        drift_count = df['drift_detected'].sum()
        drift_percent = drift_count / len(df) * 100
        st.markdown(f"**Drift detected in {drift_count} requests ({drift_percent:.1f}% of total)**")
    
    def _render_token_efficiency_analysis(self, df: pd.DataFrame):
        """
        Render token efficiency analysis.
        
        Args:
            df: DataFrame with metrics data
        """
        st.subheader("Token Efficiency Analysis")
        
        if 'tokens_in' not in df.columns or 'tokens_out' not in df.columns:
            st.info("Token count data not available.")
            return
            
        # Calculate token statistics
        token_stats = {
            'avg_tokens_in': df['tokens_in'].mean(),
            'avg_tokens_out': df['tokens_out'].mean(),
            'avg_efficiency': df['tokens_out'].sum() / df['tokens_in'].sum(),
            'min_efficiency': df['tokens_out'].min() / max(1, df['tokens_in'].max()),
            'max_efficiency': df['tokens_out'].max() / max(1, df['tokens_in'].min())
        }
        
        # Create scatter plot
        fig = px.scatter(
            df,
            x='tokens_in',
            y='tokens_out',
            color='hallucination_score',
            labels={
                'tokens_in': 'Input Tokens',
                'tokens_out': 'Output Tokens',
                'hallucination_score': 'Hallucination Score'
            },
            color_continuous_scale='RdYlGn_r',
            opacity=0.7
        )
        
        # Add reference lines for different efficiency levels
        max_tokens = max(df['tokens_in'].max(), df['tokens_out'].max())
        
        # Efficiency = 1.0 line (output = input)
        fig.add_shape(
            type="line",
            y0=0, y1=max_tokens,
            x0=0, x1=max_tokens,
            line=dict(color="rgba(255, 255, 255, 0.3)", width=1, dash="dot")
        )
        fig.add_annotation(
            x=max_tokens * 0.8, 
            y=max_tokens * 0.8,
            text="1:1",
            showarrow=False,
            font=dict(size=10, color="rgba(255, 255, 255, 0.7)")
        )
        
        # Efficiency = 0.5 line (output = input/2)
        fig.add_shape(
            type="line",
            y0=0, y1=max_tokens/2,
            x0=0, x1=max_tokens,
            line=dict(color="rgba(255, 255, 255, 0.2)", width=1, dash="dot")
        )
        fig.add_annotation(
            x=max_tokens * 0.8, 
            y=max_tokens * 0.4,
            text="1:2",
            showarrow=False,
            font=dict(size=10, color="rgba(255, 255, 255, 0.7)")
        )
        
        # Efficiency = 2.0 line (output = input*2)
        fig.add_shape(
            type="line",
            y0=0, y1=max_tokens,
            x0=0, x1=max_tokens/2,
            line=dict(color="rgba(255, 255, 255, 0.2)", width=1, dash="dot")
        )
        fig.add_annotation(
            x=max_tokens * 0.4, 
            y=max_tokens * 0.8,
            text="2:1",
            showarrow=False,
            font=dict(size=10, color="rgba(255, 255, 255, 0.7)")
        )
        
        # Customize layout
        fig.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Token efficiency summary
        st.markdown(f"""
        **Token Efficiency Summary:**
        - Average input tokens: {token_stats['avg_tokens_in']:.1f}
        - Average output tokens: {token_stats['avg_tokens_out']:.1f}
        - Average efficiency ratio: {token_stats['avg_efficiency']:.2f} (output/input)
        """)
    
    def _render_dimensionality_reduction(self, df: pd.DataFrame):
        """
        Render dimensionality reduction visualization (PCA).
        
        Args:
            df: DataFrame with metrics data
        """
        st.subheader("Request Clustering (PCA)")
        
        # Select numeric columns for PCA
        numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
        
        # Filter relevant metrics
        relevant_metrics = [
            'hallucination_score', 'fact_consistency', 'response_time_ms', 
            'system_cpu_percent', 'system_memory_bytes'
        ]
        
        # Keep only metrics that exist in the data
        metrics_to_use = [col for col in relevant_metrics if col in numeric_cols]
        
        if len(metrics_to_use) < 2:
            st.info("Not enough metrics for clustering analysis.")
            return
            
        # Standardize data for PCA
        from sklearn.preprocessing import StandardScaler
        scaled_data = StandardScaler().fit_transform(df[metrics_to_use])
        
        try:
            # Apply PCA
            pca = PCA(n_components=2)
            pca_result = pca.fit_transform(scaled_data)
            
            # Create DataFrame for visualization
            pca_df = pd.DataFrame({
                'PC1': pca_result[:, 0],
                'PC2': pca_result[:, 1],
                'hallucination_score': df['hallucination_score'] if 'hallucination_score' in df.columns else 0
            })
            
            # Create scatter plot
            fig = px.scatter(
                pca_df,
                x='PC1',
                y='PC2',
                color='hallucination_score',
                labels={
                    'PC1': 'Principal Component 1',
                    'PC2': 'Principal Component 2',
                    'hallucination_score': 'Hallucination Score'
                },
                color_continuous_scale='RdYlGn_r'
            )
            
            # Customize layout
            fig.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=40, b=20),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Add variance explained
            explained_variance = pca.explained_variance_ratio_
            st.markdown(f"""
            **Variance Explained:**
            - PC1: {explained_variance[0]*100:.1f}%
            - PC2: {explained_variance[1]*100:.1f}%
            - Total: {sum(explained_variance)*100:.1f}%
            """)
            
        except Exception as e:
            st.error(f"Error performing PCA: {str(e)}")