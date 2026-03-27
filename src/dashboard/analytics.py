"""Session merging and aggregation, adapted from feature_extract.py."""

import datetime
from typing import Callable, Dict, List, Optional, Tuple

import pandas as pd

ACTIVITY_TYPES = {
    'deep_work': {'label_include': 2, 'label_gap': 2},
    'light_work': {'label_include': 1, 'label_gap': 1},
    'wasted': {'label_include': -1, 'label_gap': -1},
}


def filter_wanted_activity(
    labels: List[int], label_include: int, label_gap: int
) -> List[bool]:
    """Boolean mask for rows matching the desired activity type.

    Adapted from feature_extract.py:199-237. Gap-filling: if a gap-type
    activity sits between two include-type activities, it's included.
    """
    mask = [False] * len(labels)

    for i in range(len(labels)):
        if labels[i] != label_include:
            continue
        mask[i] = True
        # Fill gap: if prev is gap-type and the one before is include-type
        if (i >= 2
                and labels[i - 1] == label_gap
                and labels[i - 2] == label_include):
            mask[i - 1] = True

    return mask


def extract_sessions(
    df: pd.DataFrame,
    file_date: datetime.date,
    label_include: int,
    label_gap: int,
) -> pd.DataFrame:
    """Merge consecutive same-label rows into sessions with durations.

    Adapted from feature_extract.py:131-196.
    """
    labels = df['Label'].tolist()
    mask = filter_wanted_activity(labels, label_include, label_gap)

    sessions = []
    cur_start = None
    cur_activity = ""

    for idx, row in df.iterrows():
        date_time_str = f'{row["Date"]} {row["Time"]}'
        cur_time = datetime.datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")

        if not mask[idx]:
            # End current session if one is active
            if cur_activity:
                duration = (cur_time - cur_start) / datetime.timedelta(hours=1)
                sessions.append({
                    'Date': file_date,
                    'Weekday': file_date.weekday() + 1,
                    'Activity': cur_activity,
                    'StartTime': cur_start,
                    'DurationHours': duration,
                })
                cur_activity = ""
            continue

        # Continuation of current session
        if idx > 0 and mask[idx - 1]:
            cur_activity += f'|{row["Activity"]}'
            continue

        # Start of new session
        cur_start = cur_time
        cur_activity = row["Activity"]

    # Handle session that extends to end of log (use last row time + small delta)
    if cur_activity and cur_start:
        last_time_str = f'{df.iloc[-1]["Date"]} {df.iloc[-1]["Time"]}'
        last_time = datetime.datetime.strptime(last_time_str, "%Y-%m-%d %H:%M:%S")
        duration = (last_time - cur_start) / datetime.timedelta(hours=1)
        if duration > 0:
            sessions.append({
                'Date': file_date,
                'Weekday': file_date.weekday() + 1,
                'Activity': cur_activity,
                'StartTime': cur_start,
                'DurationHours': duration,
            })

    return pd.DataFrame(sessions, columns=[
        'Date', 'Weekday', 'Activity', 'StartTime', 'DurationHours'
    ])


def process_day(df: pd.DataFrame, file_date: datetime.date) -> pd.DataFrame:
    """Run extraction passes for all activity types and concatenate."""
    dfs = []
    for act_type, params in ACTIVITY_TYPES.items():
        sessions = extract_sessions(df, file_date, **params)
        if not sessions.empty:
            sessions['Activity_Type'] = act_type
            dfs.append(sessions)

    if not dfs:
        return pd.DataFrame(columns=[
            'Date', 'Weekday', 'Activity', 'StartTime',
            'DurationHours', 'Activity_Type'
        ])
    return pd.concat(dfs, ignore_index=True)


def process_range(
    file_dict: Dict[datetime.date, str],
    read_fn: Callable,
) -> pd.DataFrame:
    """Process multiple days of logs."""
    dfs = []
    for file_date, path in file_dict.items():
        raw_df = read_fn(path)
        if raw_df.empty:
            continue
        day_df = process_day(raw_df, file_date)
        if not day_df.empty:
            dfs.append(day_df)

    if not dfs:
        return pd.DataFrame(columns=[
            'Date', 'Weekday', 'Activity', 'StartTime',
            'DurationHours', 'Activity_Type'
        ])
    return pd.concat(dfs, ignore_index=True)


def aggregate_daily(sessions: pd.DataFrame) -> pd.DataFrame:
    """Group sessions by (Date, Activity_Type), summing durations."""
    if sessions.empty:
        return sessions

    agg = sessions.groupby(['Date', 'Activity_Type']).agg(
        DurationHours=('DurationHours', 'sum'),
        Weekday=('Weekday', 'first'),
    ).reset_index()

    agg = agg.sort_values(['Date', 'Activity_Type'])
    return agg


def aggregate_total(sessions: pd.DataFrame) -> pd.DataFrame:
    """Group sessions by Activity_Type across full range."""
    if sessions.empty:
        return sessions

    agg = sessions.groupby('Activity_Type').agg(
        TotalHours=('DurationHours', 'sum'),
        MeanHoursPerDay=('DurationHours', 'mean'),
        SessionCount=('DurationHours', 'count'),
    ).reset_index()

    return agg
