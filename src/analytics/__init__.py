"""
Analytics Module
================
Provides statistical analysis and visualization:
  - Operation statistics
  - Timeline charts
  - Method comparison
  - User activity tracking
"""

from .stats import (
    create_timeline_chart,
    create_method_pie_chart,
    create_encode_decode_chart,
    create_method_comparison_chart,
    create_size_distribution_chart,
    create_hourly_heatmap,
    create_performance_chart,
    get_activity_dataframe,
    get_statistics_summary,
    get_user_detailed_stats,
)
from .ui_section import show_analytics_section

__all__ = [
    'create_timeline_chart',
    'create_method_pie_chart',
    'create_encode_decode_chart',
    'create_method_comparison_chart',
    'create_size_distribution_chart',
    'create_hourly_heatmap',
    'create_performance_chart',
    'get_activity_dataframe',
    'get_statistics_summary',
    'get_user_detailed_stats',
    'show_analytics_section',
]
