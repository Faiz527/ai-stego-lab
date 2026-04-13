"""
Analytics Module
================
Handles statistics collection, data visualization, and chart generation.
Connected to PostgreSQL database for real user statistics tracking.
"""

from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from ..db.db_utils import (
    get_timeline_data,
    get_method_distribution,
    get_encode_decode_stats,
    get_size_distribution,
    get_activity_log,
    get_operation_stats,
    get_user_operations,
    get_db_connection
)


# ============================================================================
#                    USER-SPECIFIC HELPER FUNCTIONS
# ============================================================================

def get_user_timeline_data(user_id: int, days: int = 7) -> list:
    """Get timeline data for operations over N days for a specific user."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as count
            FROM operations
            WHERE user_id = %s AND created_at >= CURRENT_TIMESTAMP - INTERVAL '%s days'
            GROUP BY DATE(created_at)
            ORDER BY DATE(created_at)
        """, (user_id, days))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [{'date': str(row[0]), 'count': row[1]} for row in results]
        
    except Exception as e:
        print(f"Error getting user timeline data: {str(e)}")
        return []


def get_user_method_distribution(user_id: int) -> dict:
    """Get distribution of operations by method for a specific user."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT method, COUNT(*) as count
            FROM operations
            WHERE user_id = %s AND method IS NOT NULL
            GROUP BY method
            ORDER BY count DESC
        """, (user_id,))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return dict(results) if results else {}
        
    except Exception as e:
        print(f"Error getting user method distribution: {str(e)}")
        return {}


def get_user_activity_log(user_id: int, limit: int = 50) -> pd.DataFrame:
    """Get activity log as pandas DataFrame for a specific user."""
    try:
        activities = get_activity_log(user_id=user_id, limit=limit)
        
        if not activities:
            return pd.DataFrame()
        
        df = pd.DataFrame(
            activities,
            columns=['ID', 'User ID', 'Action', 'Details', 'Timestamp']
        )
        
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        df = df.sort_values('Timestamp', ascending=False)
        
        return df
        
    except Exception as e:
        print(f"Error getting user activity dataframe: {str(e)}")
        return pd.DataFrame()


def get_user_operation_count(user_id: int) -> int:
    """Get total operation count for a specific user."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM operations WHERE user_id = %s", (user_id,))
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        return count
        
    except Exception as e:
        print(f"Error getting user operation count: {str(e)}")
        return 0


def get_user_size_distribution(user_id: int) -> dict:
    """Get distribution of message sizes for a specific user."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN message_length < 100 THEN 'Tiny (< 100B)'
                    WHEN message_length < 1024 THEN 'Small (100B-1KB)'
                    WHEN message_length < 10240 THEN 'Medium (1-10KB)'
                    WHEN message_length < 102400 THEN 'Large (10-100KB)'
                    ELSE 'Very Large (> 100KB)'
                END as size_category,
                COUNT(*) as count
            FROM operations
            WHERE user_id = %s AND message_length IS NOT NULL
            GROUP BY 
                CASE 
                    WHEN message_length < 100 THEN 'Tiny (< 100B)'
                    WHEN message_length < 1024 THEN 'Small (100B-1KB)'
                    WHEN message_length < 10240 THEN 'Medium (1-10KB)'
                    WHEN message_length < 102400 THEN 'Large (10-100KB)'
                    ELSE 'Very Large (> 100KB)'
                END
        """, (user_id,))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return dict(results) if results else {}
        
    except Exception as e:
        print(f"Error getting user size distribution: {str(e)}")
        return {}


def get_user_detailed_stats(user_id: int) -> dict:
    """
    Get comprehensive statistics for a user.
    
    Returns detailed metrics including:
    - Total operations
    - Encode vs decode counts
    - Average encoding time
    - Total data processed
    - Most used method
    - Success rate
    - Activity streak
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get comprehensive stats in one query
        # Check operation_type column: 'encode' or 'decode'
        cursor.execute("""
            SELECT 
                COUNT(*) as total_ops,
                COUNT(CASE WHEN status = 'success' THEN 1 END) as successful_ops,
                COUNT(CASE WHEN operation_type = 'encode' THEN 1 END) as encode_count,
                COUNT(CASE WHEN operation_type = 'decode' THEN 1 END) as decode_count,
                COALESCE(AVG(encoding_time), 0) as avg_time,
                COALESCE(SUM(message_length), 0) as total_bytes,
                MAX(created_at) as last_activity,
                MIN(created_at) as first_activity
            FROM operations
            WHERE user_id = %s
        """, (user_id,))
        
        row = cursor.fetchone()
        
        # Get most used method
        cursor.execute("""
            SELECT method, COUNT(*) as cnt
            FROM operations
            WHERE user_id = %s AND method IS NOT NULL
            GROUP BY method
            ORDER BY cnt DESC
            LIMIT 1
        """, (user_id,))
        
        method_row = cursor.fetchone()
        
        # Get activity streak (consecutive days up to today)
        cursor.execute("""
            WITH daily_activity AS (
                SELECT DISTINCT DATE(created_at) as activity_date
                FROM operations
                WHERE user_id = %s
                ORDER BY activity_date DESC
            ),
            numbered AS (
                SELECT 
                    activity_date,
                    ROW_NUMBER() OVER (ORDER BY activity_date DESC) as rn
                FROM daily_activity
            )
            SELECT COUNT(*) as streak
            FROM numbered
            WHERE activity_date >= CURRENT_DATE - (rn - 1)::int
              AND activity_date <= CURRENT_DATE
        """, (user_id,))
        
        streak_row = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if row:
            total_ops = row[0] or 0
            successful_ops = row[1] or 0
            encode_count = row[2] or 0
            decode_count = row[3] or 0
            avg_time = row[4] or 0
            total_bytes = row[5] or 0
            last_activity = row[6]
            first_activity = row[7]
            
            # Calculate success rate
            success_rate = (successful_ops / total_ops * 100) if total_ops > 0 else 0
            
            # Format total bytes
            if total_bytes >= 1024 * 1024:
                total_data = f"{total_bytes / (1024 * 1024):.1f} MB"
            elif total_bytes >= 1024:
                total_data = f"{total_bytes / 1024:.1f} KB"
            else:
                total_data = f"{int(total_bytes)} B"
            
            # Calculate days active
            if last_activity and first_activity:
                days_active = (last_activity - first_activity).days + 1
            else:
                days_active = 0
            
            return {
                'total_operations': total_ops,
                'encode_count': encode_count,
                'decode_count': decode_count,
                'success_rate': round(success_rate, 1),
                'avg_encoding_time': round(float(avg_time), 2),
                'total_data_processed': total_data,
                'favorite_method': method_row[0] if method_row else 'N/A',
                'activity_streak': streak_row[0] if streak_row else 0,
                'last_activity': last_activity,
                'first_activity': first_activity,
                'days_active': days_active
            }
        
        return {}
        
    except Exception as e:
        print(f"Error getting user detailed stats: {str(e)}")
        return {}


def get_user_hourly_activity(user_id: int) -> dict:
    """Get activity distribution by hour of day."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                EXTRACT(HOUR FROM created_at)::int as hour,
                COUNT(*) as count
            FROM operations
            WHERE user_id = %s
            GROUP BY hour
            ORDER BY hour
        """, (user_id,))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Fill in missing hours with 0
        hourly = {i: 0 for i in range(24)}
        for hour, count in results:
            hourly[hour] = count
        
        return hourly
        
    except Exception as e:
        print(f"Error getting hourly activity: {str(e)}")
        return {}


def get_user_weekly_activity(user_id: int) -> dict:
    """Get activity distribution by day of week."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                EXTRACT(DOW FROM created_at)::int as dow,
                COUNT(*) as count
            FROM operations
            WHERE user_id = %s
            GROUP BY dow
            ORDER BY dow
        """, (user_id,))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        weekly = {days[i]: 0 for i in range(7)}
        for dow, count in results:
            weekly[days[dow]] = count
        
        return weekly
        
    except Exception as e:
        print(f"Error getting weekly activity: {str(e)}")
        return {}


def get_user_performance_trend(user_id: int, days: int = 30) -> list:
    """Get encoding time performance trend over time."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                DATE(created_at) as date,
                AVG(encoding_time) as avg_time,
                COUNT(*) as operations
            FROM operations
            WHERE user_id = %s 
              AND created_at >= CURRENT_TIMESTAMP - INTERVAL '%s days'
              AND encoding_time IS NOT NULL
            GROUP BY DATE(created_at)
            ORDER BY date
        """, (user_id, days))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [{'date': str(row[0]), 'avg_time': float(row[1]), 'count': row[2]} for row in results]
        
    except Exception as e:
        print(f"Error getting performance trend: {str(e)}")
        return []


# ============================================================================
#                         CHART CREATION FUNCTIONS
# ============================================================================

def create_timeline_chart(user_id: int = None, stats_data: dict = None) -> go.Figure:
    """Create timeline chart of operations over last 7 days."""
    try:
        if user_id:
            timeline_data = get_user_timeline_data(user_id, days=7)
        else:
            timeline_data = get_timeline_data(days=7)
        
        # Generate date range for last 7 days
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=6)
        date_range = [(start_date + timedelta(days=i)).isoformat() for i in range(7)]
        
        # Map existing data
        date_counts = {item['date']: item['count'] for item in timeline_data}
        counts = [date_counts.get(d, 0) for d in date_range]
        
        fig = go.Figure()
        
        # Add area fill
        fig.add_trace(go.Scatter(
            x=date_range,
            y=counts,
            mode='lines',
            fill='tozeroy',
            fillcolor='rgba(35, 134, 54, 0.2)',
            line=dict(color='#238636', width=0),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Add line with markers
        fig.add_trace(go.Scatter(
            x=date_range,
            y=counts,
            mode='lines+markers',
            name='Operations',
            line=dict(color='#238636', width=3),
            marker=dict(size=10, color='#238636', line=dict(color='#0D1117', width=2)),
            hovertemplate='<b>%{x}</b><br>Operations: %{y}<extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(text="Activity Timeline (Last 7 Days)", font=dict(size=16)),
            xaxis_title="Date",
            yaxis_title="Operations",
            template="plotly_dark",
            hovermode='x unified',
            plot_bgcolor='#0D1117',
            paper_bgcolor='#0D1117',
            font=dict(color='#C9D1D9'),
            margin=dict(l=40, r=20, t=50, b=40),
            yaxis=dict(gridcolor='#21262D', rangemode='tozero'),
            xaxis=dict(gridcolor='#21262D')
        )
        
        return fig
        
    except Exception as e:
        print(f"Error creating timeline chart: {str(e)}")
        return go.Figure()


def create_method_pie_chart(user_id: int = None, stats_data: dict = None) -> go.Figure:
    """Create pie chart showing method distribution."""
    try:
        if user_id:
            method_dist = get_user_method_distribution(user_id)
        else:
            method_dist = get_method_distribution()
        
        if not method_dist:
            fig = go.Figure()
            fig.add_annotation(
                text="No data yet",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color='#8B949E')
            )
            fig.update_layout(
                title="Method Distribution",
                template="plotly_dark",
                plot_bgcolor='#0D1117',
                paper_bgcolor='#0D1117'
            )
            return fig
        
        methods = list(method_dist.keys())
        counts = list(method_dist.values())
        
        colors = {
            'LSB': '#238636',
            'Hybrid DCT': '#1F6FEB',
            'Hybrid DWT': '#8957E5',
            'DCT': '#1F6FEB',
            'DWT': '#8957E5'
        }
        
        marker_colors = [colors.get(m, '#58A6FF') for m in methods]
        
        fig = go.Figure(data=[go.Pie(
            labels=methods,
            values=counts,
            marker=dict(colors=marker_colors, line=dict(color='#0D1117', width=2)),
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>',
            textinfo='label+percent',
            textfont=dict(size=12),
            hole=0.4
        )])
        
        fig.update_layout(
            title=dict(text="Method Distribution", font=dict(size=16)),
            template="plotly_dark",
            plot_bgcolor='#0D1117',
            paper_bgcolor='#0D1117',
            font=dict(color='#C9D1D9'),
            margin=dict(l=20, r=20, t=50, b=20),
            showlegend=True,
            legend=dict(orientation='h', yanchor='bottom', y=-0.1, xanchor='center', x=0.5)
        )
        
        return fig
        
    except Exception as e:
        print(f"Error creating method pie chart: {str(e)}")
        return go.Figure()


def create_encode_decode_chart(user_id: int = None) -> go.Figure:
    """Create bar chart comparing encode vs decode operations."""
    try:
        if user_id:
            stats = get_user_detailed_stats(user_id)
            encode_count = stats.get('encode_count', 0)
            decode_count = stats.get('decode_count', 0)
        else:
            ed_stats = get_encode_decode_stats()
            encode_count = ed_stats.get('Encode', 0)
            decode_count = ed_stats.get('Decode', 0)
        
        fig = go.Figure(data=[
            go.Bar(
                x=['Encode', 'Decode'],
                y=[encode_count, decode_count],
                marker=dict(
                    color=['#238636', '#1F6FEB'],
                    line=dict(color='#0D1117', width=1)
                ),
                text=[encode_count, decode_count],
                textposition='auto',
                textfont=dict(size=14, color='white'),
                hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title=dict(text="Encode vs Decode Operations", font=dict(size=16)),
            xaxis_title="Operation Type",
            yaxis_title="Count",
            template="plotly_dark",
            plot_bgcolor='#0D1117',
            paper_bgcolor='#0D1117',
            font=dict(color='#C9D1D9'),
            margin=dict(l=40, r=20, t=50, b=40),
            yaxis=dict(gridcolor='#21262D', rangemode='tozero'),
            showlegend=False
        )
        
        return fig
        
    except Exception as e:
        print(f"Error creating encode/decode chart: {str(e)}")
        return go.Figure()


def create_hourly_heatmap(user_id: int) -> go.Figure:
    """Create heatmap showing activity by hour and day."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                EXTRACT(DOW FROM created_at)::int as dow,
                EXTRACT(HOUR FROM created_at)::int as hour,
                COUNT(*) as count
            FROM operations
            WHERE user_id = %s
            GROUP BY dow, hour
        """, (user_id,))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Create matrix
        days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        hours = [f"{h:02d}:00" for h in range(24)]
        
        matrix = np.zeros((7, 24))
        for dow, hour, count in results:
            matrix[dow][hour] = count
        
        fig = go.Figure(data=go.Heatmap(
            z=matrix,
            x=hours,
            y=days,
            colorscale=[
                [0, '#0D1117'],
                [0.25, '#0E4429'],
                [0.5, '#006D32'],
                [0.75, '#26A641'],
                [1, '#39D353']
            ],
            hovertemplate='<b>%{y} %{x}</b><br>Operations: %{z}<extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(text="Activity Heatmap", font=dict(size=16)),
            xaxis_title="Hour",
            yaxis_title="Day",
            template="plotly_dark",
            plot_bgcolor='#0D1117',
            paper_bgcolor='#0D1117',
            font=dict(color='#C9D1D9'),
            margin=dict(l=60, r=20, t=50, b=40),
            xaxis=dict(tickangle=-45, dtick=3)
        )
        
        return fig
        
    except Exception as e:
        print(f"Error creating heatmap: {str(e)}")
        return go.Figure()


def create_performance_chart(user_id: int) -> go.Figure:
    """Create chart showing encoding time performance."""
    try:
        performance_data = get_user_performance_trend(user_id, days=30)
        
        if not performance_data:
            fig = go.Figure()
            fig.add_annotation(
                text="No performance data yet",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color='#8B949E')
            )
            fig.update_layout(
                title="Encoding Performance",
                template="plotly_dark",
                plot_bgcolor='#0D1117',
                paper_bgcolor='#0D1117'
            )
            return fig
        
        dates = [d['date'] for d in performance_data]
        times = [d['avg_time'] for d in performance_data]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=times,
            mode='lines+markers',
            name='Avg. Time',
            line=dict(color='#F78166', width=2),
            marker=dict(size=8, color='#F78166'),
            hovertemplate='<b>%{x}</b><br>Avg Time: %{y:.2f}s<extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(text="Encoding Performance Trend", font=dict(size=16)),
            xaxis_title="Date",
            yaxis_title="Avg. Encoding Time (seconds)",
            template="plotly_dark",
            plot_bgcolor='#0D1117',
            paper_bgcolor='#0D1117',
            font=dict(color='#C9D1D9'),
            margin=dict(l=40, r=20, t=50, b=40),
            yaxis=dict(gridcolor='#21262D'),
            xaxis=dict(gridcolor='#21262D')
        )
        
        return fig
        
    except Exception as e:
        print(f"Error creating performance chart: {str(e)}")
        return go.Figure()


def create_size_distribution_chart(user_id: int = None, stats_data: dict = None) -> go.Figure:
    """Create chart showing message size distribution."""
    try:
        if user_id:
            size_dist = get_user_size_distribution(user_id)
        else:
            size_dist = get_size_distribution()
        
        if not size_dist:
            fig = go.Figure()
            fig.add_annotation(
                text="No data yet",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color='#8B949E')
            )
            fig.update_layout(
                title="Message Size Distribution",
                template="plotly_dark",
                plot_bgcolor='#0D1117',
                paper_bgcolor='#0D1117'
            )
            return fig
        
        categories = list(size_dist.keys())
        values = list(size_dist.values())
        
        colors = ['#238636', '#26A641', '#39D353', '#69DB7C', '#98F3A9']
        
        fig = go.Figure(data=[
            go.Bar(
                x=categories,
                y=values,
                marker=dict(color=colors[:len(categories)], line=dict(color='#0D1117', width=1)),
                text=values,
                textposition='auto',
                textfont=dict(size=12),
                hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title=dict(text="Message Size Distribution", font=dict(size=16)),
            xaxis_title="Size Category",
            yaxis_title="Count",
            template="plotly_dark",
            plot_bgcolor='#0D1117',
            paper_bgcolor='#0D1117',
            font=dict(color='#C9D1D9'),
            margin=dict(l=40, r=20, t=50, b=60),
            yaxis=dict(gridcolor='#21262D', rangemode='tozero'),
            xaxis=dict(tickangle=-20),
            showlegend=False
        )
        
        return fig
        
    except Exception as e:
        print(f"Error creating size distribution chart: {str(e)}")
        return go.Figure()


def create_method_comparison_chart() -> go.Figure:
    """Create comparison chart of all three methods."""
    try:
        methods = ['LSB', 'Hybrid DCT', 'Hybrid DWT']
        
        fig = go.Figure()
        
        # Capacity bars
        fig.add_trace(go.Bar(
            name='Capacity (KB)',
            x=methods,
            y=[180, 60, 15],
            marker_color='#238636',
            text=['180 KB', '60 KB', '15 KB'],
            textposition='auto'
        ))
        
        fig.update_layout(
            title=dict(text="Method Capacity Comparison", font=dict(size=16)),
            xaxis_title="Method",
            yaxis_title="Capacity (KB)",
            template="plotly_dark",
            plot_bgcolor='#0D1117',
            paper_bgcolor='#0D1117',
            font=dict(color='#C9D1D9'),
            margin=dict(l=40, r=20, t=50, b=40),
            yaxis=dict(gridcolor='#21262D'),
            showlegend=False
        )
        
        return fig
        
    except Exception as e:
        print(f"Error creating comparison chart: {str(e)}")
        return go.Figure()


# ============================================================================
#                         DATA RETRIEVAL FUNCTIONS
# ============================================================================

def get_activity_dataframe(user_id: int = None, limit: int = 50) -> pd.DataFrame:
    """Get activity log as pandas DataFrame."""
    try:
        if user_id:
            return get_user_activity_log(user_id, limit=limit)
        else:
            activities = get_activity_log(limit=limit)
            
            if not activities:
                return pd.DataFrame()
            
            df = pd.DataFrame(
                activities,
                columns=['ID', 'User ID', 'Action', 'Details', 'Timestamp']
            )
            
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])
            df = df.sort_values('Timestamp', ascending=False)
            
            return df
        
    except Exception as e:
        print(f"Error getting activity dataframe: {str(e)}")
        return pd.DataFrame()


def get_statistics_summary(user_id: int = None) -> dict:
    """
    Get statistics summary (global or user-specific).
    
    Returns a clean dict with displayable values only.
    """
    try:
        if user_id:
            detailed = get_user_detailed_stats(user_id)
            return {
                'total_operations': detailed.get('total_operations', 0),
                'encode_count': detailed.get('encode_count', 0),
                'decode_count': detailed.get('decode_count', 0),
                'success_rate': f"{detailed.get('success_rate', 0)}%",
                'avg_encoding_time': f"{detailed.get('avg_encoding_time', 0)}s",
                'total_data_processed': detailed.get('total_data_processed', '0 B'),
                'favorite_method': detailed.get('favorite_method', 'N/A'),
                'activity_streak': detailed.get('activity_streak', 0),
                'days_active': detailed.get('days_active', 0)
            }
        else:
            from ..db.db_utils import get_user_count, get_operation_count
            
            return {
                'total_users': get_user_count(),
                'total_operations': get_operation_count()
            }
        
    except Exception as e:
        print(f"Error getting statistics summary: {str(e)}")
        return {}
