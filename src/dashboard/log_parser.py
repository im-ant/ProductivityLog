"""Raw TSV log reading with inline [z] label extraction."""

import datetime
import glob
import os
import re
from typing import Dict, Optional, Tuple

import pandas as pd

# Default path to raw log directory
DEFAULT_LOG_DIR = 'INPUT_RAW_DIR/daily_logs'

# Regex to match [z] prefix where z is an integer (possibly negative)
_LABEL_RE = re.compile(r'^\[(-?\d+)\]\s*(.*)')


def filepath_to_date(path: str) -> datetime.date:
    """Parse date from filename like YYYY-MM-DD_log.tsv."""
    filename = os.path.basename(path)
    date_str = filename.split('_')[0]
    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()


def parse_label(activity: str) -> Tuple[int, str]:
    """Extract [z] prefix from activity string.

    Returns (label, cleaned_text). Defaults to (0, raw_text) if no label found
    (pre-label era logs).
    """
    if not isinstance(activity, str):
        return (0, str(activity))
    m = _LABEL_RE.match(activity)
    if m:
        return (int(m.group(1)), m.group(2))
    return (0, activity)


def read_raw_log(path: str) -> pd.DataFrame:
    """Read a raw TSV log file and add Label column inline."""
    df = pd.read_csv(path, delimiter='\t')
    if 'Activity' not in df.columns:
        return pd.DataFrame(columns=['Date', 'Time', 'Activity', 'Label'])

    labels_and_text = df['Activity'].apply(parse_label)
    df['Label'] = labels_and_text.apply(lambda x: x[0])
    df['Activity'] = labels_and_text.apply(lambda x: x[1])
    return df


def get_raw_files(
    log_dir: str = DEFAULT_LOG_DIR,
    date_range: Optional[Tuple[datetime.date, datetime.date]] = None,
) -> Dict[datetime.date, str]:
    """Glob raw log files and filter by date range.

    Returns sorted dict mapping date -> file path.
    """
    all_paths = glob.glob(os.path.join(log_dir, '*_log.tsv'))
    file_dict = {}

    for path in all_paths:
        try:
            file_date = filepath_to_date(path)
        except (ValueError, IndexError):
            continue
        if date_range and not (date_range[0] <= file_date <= date_range[1]):
            continue
        file_dict[file_date] = path

    return dict(sorted(file_dict.items()))


def get_today_log(log_dir: str = DEFAULT_LOG_DIR) -> Optional[pd.DataFrame]:
    """Read today's log file, or return None if it doesn't exist."""
    today = datetime.date.today()
    filename = f"{today.strftime('%Y-%m-%d')}_log.tsv"
    path = os.path.join(log_dir, filename)
    if os.path.exists(path):
        return read_raw_log(path)
    return None
