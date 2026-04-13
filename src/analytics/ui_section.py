"""
Analytics UI Section
====================
Handles all analytics visualization and display logic.
Moved from ui_components.py for better code organization.
"""

import streamlit as st
import pandas as pd
import logging

from src.analytics.stats import (
    create_timeline_chart,
    create_method_pie_chart,
    create_encode_decode_chart,
    create_method_comparison_chart,
    get_statistics_summary,
    get_activity_dataframe,
    create_size_distribution_chart,
    create_hourly_heatmap,
    create_performance_chart,
    get_user_detailed_stats
)
from src.ui.reusable_components import (
    show_warning, show_info, render_step
)

logger = logging.getLogger(__name__)


def show_analytics_section():
    """Display statistics and analytics dashboard with refresh capability."""
    
    # Header with refresh button
    col1, col2 = st.columns([0.85, 0.15])
    
    with col1:
        st.markdown("""
            <div class="animate-fade-in-down">
                <h2>📊 Analytics Dashboard</h2>
                <p style="color: #8B949E; margin-bottom: 1rem;">View your steganography activity and statistics</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Refresh", key="analytics_refresh_btn", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    st.divider()
    
    # Get current user_id
    user_id = st.session_state.get('user_id', None)
    
    if not user_id:
        show_warning("Please log in to view your analytics dashboard.")
        return
    
    # ─────────────────────────────────────────────────────────────
    # Summary Metrics Section
    # ─────────────────────────────────────────────────────────────
    
    st.markdown("### 📈 Overview")
    
    stats = get_user_detailed_stats(user_id)
    
    if stats and stats.get('total_operations', 0) > 0:
        _display_summary_metrics(stats)
        
        st.divider()
        
        # ─────────────────────────────────────────────────────────────
        # Charts Section
        # ─────────────────────────────────────────────────────────────
        
        st.markdown("### 📉 Activity Charts")
        _display_activity_charts(user_id)
        
        st.divider()
        
        # ─────────────────────────────────────────────────────────────
        # Advanced Analytics
        # ─────────────────────────────────────────────────────────────
        
        st.markdown("### 🔬 Advanced Analytics")
        _display_advanced_analytics(user_id)
        
        st.divider()
        
        # ─────────────────────────────────────────────────────────────
        # Activity Log Table
        # ─────────────────────────────────────────────────────────────
        
        st.markdown("### 📋 Recent Activity Log")
        _display_activity_log(user_id)
    
    else:
        _display_empty_state()


def _display_summary_metrics(stats: dict):
    """Display summary metric cards."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Operations",
            stats.get('total_operations', 0),
            delta=None,
            delta_color="normal"
        )
    with col2:
        st.metric("Encodes", stats.get('encode_count', 0))
    with col3:
        st.metric("Decodes", stats.get('decode_count', 0))
    with col4:
        st.metric("Favorite Method", stats.get('favorite_method', 'N/A'))
    
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        st.metric("Success Rate", f"{stats.get('success_rate', 0)}%")
    with col6:
        st.metric("Avg. Time", f"{stats.get('avg_encoding_time', 0)}s")
    with col7:
        st.metric("Data Processed", stats.get('total_data_processed', '0 B'))
    with col8:
        st.metric("Days Active", stats.get('days_active', 0))


def _display_activity_charts(user_id: int):
    """Display activity timeline and method distribution charts."""
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        try:
            fig_timeline = create_timeline_chart(user_id=user_id)
            st.plotly_chart(fig_timeline, use_container_width=True)
        except Exception as e:
            st.error(f"Error loading timeline chart: {e}")
    
    with chart_col2:
        try:
            fig_pie = create_method_pie_chart(user_id=user_id)
            st.plotly_chart(fig_pie, use_container_width=True)
        except Exception as e:
            st.error(f"Error loading method distribution: {e}")
    
    # Second row of charts
    chart_col3, chart_col4 = st.columns(2)
    
    with chart_col3:
        try:
            fig_encode_decode = create_encode_decode_chart(user_id=user_id)
            st.plotly_chart(fig_encode_decode, use_container_width=True)
        except Exception as e:
            st.error(f"Error loading encode/decode chart: {e}")
    
    with chart_col4:
        try:
            fig_size = create_size_distribution_chart(user_id=user_id)
            st.plotly_chart(fig_size, use_container_width=True)
        except Exception as e:
            st.error(f"Error loading size distribution: {e}")


def _display_advanced_analytics(user_id: int):
    """Display advanced analytics (heatmap, performance, comparison)."""
    chart_col5, chart_col6 = st.columns(2)
    
    with chart_col5:
        try:
            fig_heatmap = create_hourly_heatmap(user_id=user_id)
            st.plotly_chart(fig_heatmap, use_container_width=True)
        except Exception as e:
            st.error(f"Error loading activity heatmap: {e}")
    
    with chart_col6:
        try:
            fig_perf = create_performance_chart(user_id=user_id)
            st.plotly_chart(fig_perf, use_container_width=True)
        except Exception as e:
            st.error(f"Error loading performance chart: {e}")
    
    # Method comparison (full width)
    st.markdown("### ⚖️ Method Comparison")
    try:
        fig_compare = create_method_comparison_chart()
        st.plotly_chart(fig_compare, use_container_width=True)
    except Exception as e:
        st.error(f"Error loading method comparison: {e}")


def _display_activity_log(user_id: int):
    """Display activity log table with search functionality."""
    try:
        activity_df = get_activity_dataframe(user_id=user_id, limit=50)
        
        if not activity_df.empty:
            # Search filter
            search_term = st.text_input(
                "🔍 Search activity log",
                placeholder="Filter by action or details...",
                key="activity_search"
            )
            
            if search_term:
                mask = (
                    activity_df['Action'].str.contains(search_term, case=False, na=False) |
                    activity_df['Details'].str.contains(search_term, case=False, na=False)
                )
                filtered_df = activity_df[mask]
            else:
                filtered_df = activity_df
            
            # Display dataframe with styling
            st.dataframe(
                filtered_df[['Action', 'Details', 'Timestamp']],
                use_container_width=True,
                hide_index=True,
                column_config={
                    'Action': st.column_config.TextColumn("Action", width="medium"),
                    'Details': st.column_config.TextColumn("Details", width="large"),
                    'Timestamp': st.column_config.DatetimeColumn("Time", format="DD/MM/YYYY HH:mm")
                }
            )
            
            # Summary
            st.caption(f"📊 Showing {len(filtered_df)} of {len(activity_df)} entries")
        else:
            show_info("No activity log entries found.")
    
    except Exception as e:
        st.error(f"Error loading activity log: {e}")
        logger.error(f"Activity log error: {e}", exc_info=True)


def _display_empty_state():
    """Display empty state when no operations exist."""
    st.markdown("""
        <div class="card" style="text-align: center; padding: 3rem;">
            <p style="font-size: 3rem;">📊</p>
            <p style="color: #8B949E; font-size: 1.2rem;">No operations recorded yet</p>
            <p style="color: #6E7681;">Start encoding or decoding images to see your analytics here!</p>
        </div>
    """, unsafe_allow_html=True)