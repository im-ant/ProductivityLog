"""Plotly figure builders for the dashboard."""

import pandas as pd
import plotly
import plotly.graph_objects as go

# Color scheme matching feature_extract.py
COLORS = {
    'deep_work': '#1f77b4',    # blue
    'light_work': '#2ca02c',   # green
    'wasted': '#d62728',       # red
}

ORDERED_TYPES = ['deep_work', 'light_work', 'wasted']
NICE_NAMES = {'deep_work': 'Deep Work', 'light_work': 'Light Work', 'wasted': 'Wasted'}


def _fig_to_json(fig: go.Figure) -> str:
    return plotly.io.to_json(fig)


def today_breakdown_bar(daily_agg: pd.DataFrame) -> str:
    """Horizontal stacked bar of today's hours by activity type."""
    fig = go.Figure()

    for act_type in ORDERED_TYPES:
        subset = daily_agg[daily_agg['Activity_Type'] == act_type]
        hours = subset['DurationHours'].sum() if not subset.empty else 0
        fig.add_trace(go.Bar(
            y=['Today'],
            x=[hours],
            name=NICE_NAMES.get(act_type, act_type),
            orientation='h',
            marker_color=COLORS.get(act_type, '#999'),
            text=f'{hours:.1f}h',
            textposition='inside',
        ))

    fig.update_layout(
        barmode='stack',
        title='Hours by Activity Type',
        xaxis_title='Hours',
        height=200,
        margin=dict(l=60, r=20, t=40, b=30),
        legend=dict(orientation='h', yanchor='bottom', y=1.02),
    )
    return _fig_to_json(fig)


def today_timeline(sessions: pd.DataFrame) -> str:
    """Gantt-style timeline of today's sessions."""
    fig = go.Figure()

    if sessions.empty:
        fig.update_layout(title='No sessions recorded today', height=300)
        return _fig_to_json(fig)

    for act_type in ORDERED_TYPES:
        subset = sessions[sessions['Activity_Type'] == act_type].copy()
        if subset.empty:
            continue

        for _, row in subset.iterrows():
            start = row['StartTime']
            end = start + pd.Timedelta(hours=row['DurationHours'])
            fig.add_trace(go.Bar(
                x=[row['DurationHours']],
                y=[NICE_NAMES.get(act_type, act_type)],
                orientation='h',
                base=[start.hour + start.minute / 60],
                marker_color=COLORS.get(act_type, '#999'),
                name=NICE_NAMES.get(act_type, act_type),
                showlegend=False,
                hovertext=f'{row["Activity"][:50]}<br>{row["DurationHours"]:.1f}h',
                hoverinfo='text',
            ))

    fig.update_layout(
        title='Session Timeline',
        xaxis_title='Hour of Day',
        xaxis=dict(range=[6, 24], dtick=2),
        barmode='stack',
        height=250,
        margin=dict(l=100, r=20, t=40, b=30),
    )
    return _fig_to_json(fig)


def range_stacked_bar(daily_agg: pd.DataFrame) -> str:
    """Vertical stacked bars, x=date, y=hours, color=activity type."""
    fig = go.Figure()

    if daily_agg.empty:
        fig.update_layout(title='No data for selected range', height=400)
        return _fig_to_json(fig)

    for act_type in ORDERED_TYPES:
        subset = daily_agg[daily_agg['Activity_Type'] == act_type]
        if subset.empty:
            continue
        fig.add_trace(go.Bar(
            x=subset['Date'].astype(str),
            y=subset['DurationHours'],
            name=NICE_NAMES.get(act_type, act_type),
            marker_color=COLORS.get(act_type, '#999'),
        ))

    fig.update_layout(
        barmode='stack',
        title='Daily Activity Breakdown',
        xaxis_title='Date',
        yaxis_title='Hours',
        height=450,
        margin=dict(l=60, r=20, t=40, b=80),
        xaxis_tickangle=-45,
        legend=dict(orientation='h', yanchor='bottom', y=1.02),
    )
    return _fig_to_json(fig)


def range_trend_lines(daily_agg: pd.DataFrame) -> str:
    """7-day rolling average line chart per activity type."""
    fig = go.Figure()

    if daily_agg.empty:
        fig.update_layout(title='No data for selected range', height=400)
        return _fig_to_json(fig)

    for act_type in ORDERED_TYPES:
        subset = daily_agg[daily_agg['Activity_Type'] == act_type].copy()
        if subset.empty:
            continue

        subset = subset.sort_values('Date')
        subset['Rolling'] = subset['DurationHours'].rolling(7, min_periods=1).mean()

        fig.add_trace(go.Scatter(
            x=subset['Date'].astype(str),
            y=subset['Rolling'],
            name=f'{NICE_NAMES.get(act_type, act_type)} (7d avg)',
            line=dict(color=COLORS.get(act_type, '#999'), width=2),
            mode='lines',
        ))

    fig.update_layout(
        title='7-Day Rolling Average',
        xaxis_title='Date',
        yaxis_title='Hours',
        height=400,
        margin=dict(l=60, r=20, t=40, b=80),
        xaxis_tickangle=-45,
        legend=dict(orientation='h', yanchor='bottom', y=1.02),
    )
    return _fig_to_json(fig)


def summary_pie(total_agg: pd.DataFrame) -> str:
    """Pie chart of total hours by activity type."""
    fig = go.Figure()

    if total_agg.empty:
        fig.update_layout(title='No data', height=400)
        return _fig_to_json(fig)

    labels = [NICE_NAMES.get(t, t) for t in total_agg['Activity_Type']]
    colors = [COLORS.get(t, '#999') for t in total_agg['Activity_Type']]

    fig.add_trace(go.Pie(
        labels=labels,
        values=total_agg['TotalHours'],
        marker_colors=colors,
        textinfo='label+percent',
        hovertemplate='%{label}: %{value:.1f} hours<extra></extra>',
    ))

    fig.update_layout(
        title='Activity Distribution',
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    return _fig_to_json(fig)
