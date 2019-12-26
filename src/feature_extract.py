# ============================================================================
# Extract features for downstream processing
#
# Requires: python 3.7+
#
# Author: Anthony Chen
# ============================================================================

import argparse
import datetime
import glob
import os
from typing import List, Tuple, Mapping

import pandas as pd

WORK_DF_COLS = ['Date', 'Weekday', 'Activity', 'StartTime', 'DurationHours']


def _filepath2date(file_path: str) -> datetime.date:
    """
    Helper method that converts a file path to a date object

    :return: datetime.date object
    """

    # Parse the file path down to just the date string
    # example path: ../labelled_logs/labelled_2019-11-26_log.tsv
    file_name = file_path.split('/')[-1]
    file_date = file_name.split('_')[1]

    # Create object and return
    return datetime.datetime.strptime(file_date, "%Y-%m-%d").date()


def get_file_list(dir_path: str, date_ranges: Tuple[datetime.date]
                  ) -> Mapping[datetime.date, str]:
    """
    Get the list of files in the allowable date range

    :param dir_path: path to the labelled directory
    :param date_ranges: 2-tuple of datetime.date object denoting the date range
    :return: sorted dictionary mapping date to file path strings
    """

    # ==
    # Helper method to check if date is within range
    def _in_date_ranges(cur_date: datetime.date):
        if date_ranges is None:
            return True
        if date_ranges[0] <= cur_date <= date_ranges[1]:
            return True
        return False

    # ==
    # Get all files
    all_file_paths = glob.glob(os.path.join(dir_path, '*.tsv'))

    file_dict = {}

    # ==
    # Filter files and their date ranges
    for file_path in all_file_paths:
        # Get date and skip if outside of desirable ranges
        cur_file_date = _filepath2date(file_path)
        if not _in_date_ranges(cur_file_date):
            continue

        # Add file date and file path to list
        file_dict[cur_file_date] = file_path

    # ==
    # Sort by date and output
    file_dict = {k: file_dict[k] for k in sorted(file_dict)}
    return file_dict


def read_extract_files(file_dict: Mapping[datetime.date, str]
                       ) -> pd.DataFrame:
    """
    Read a dictionary of file dates -> paths, generate a Pandas DataFrame which
    summarizes over the working hours of those logs

    :param file_dict: TODO write these
    :return:
    """

    # ==
    # Initialize dataframe for output
    work_df = pd.DataFrame(data=None, columns=WORK_DF_COLS)

    # ==
    # Iterate over the date range in increment of one day
    cur_iter_day = list(file_dict.keys())[0]
    final_iter_day = list(file_dict.keys())[-1]

    # Iterate
    while cur_iter_day <= final_iter_day:
        #
        print(cur_iter_day)

        # ==
        # If no record exists for this day
        # NOTE: for now, skipped day. TODO maybe handle this in future
        if cur_iter_day not in file_dict:
            cur_iter_day += datetime.timedelta(days=1)
            continue

        # ==
        # If this day has a record

        # Format record
        cur_raw_df = pd.read_csv(file_dict[cur_iter_day], delimiter='\t')
        cur_day_df = read_extract_file(cur_raw_df, cur_iter_day)

        # Append to DataFrame
        work_df = pd.concat([work_df, cur_day_df])

        cur_iter_day += datetime.timedelta(days=1)

    work_df = work_df.reset_index(drop=True)
    return work_df


def read_extract_file(raw_df: pd.DataFrame,
                      file_date: datetime.date) -> pd.DataFrame:
    """
    The MAIN method to filter a single daily log (as a pd.DataFrame) into a
    feature-extracted output df, with the header columns specified by
    WORK_DF_COLS

    :param raw_df: the input raw df denoting a single day's log
    :param file_date: the date of the current log
    :return:  output feature extracted df
    """
    # ==
    # Construct output dicitonary (to be made into df)
    work_dict = {k: [] for k in WORK_DF_COLS}

    # ==
    # Get the mask of activity (labels) we want to filter for
    act_mask = filter_wanted_activity(raw_df, col_name='Label',
                                      label_include=2, label_gap=1)

    # ==
    # Extract the activities we want to filter for
    cur_starttime = datetime.datetime(1000, 1, 1, 0, 0, 0)
    cur_activity = ""
    for index, row in raw_df.iterrows():
        # Compute the time of this activity
        date_time_str = f'{row["Date"]} {row["Time"]}'
        cur_act_time = datetime.datetime.strptime(date_time_str,
                                                  "%Y-%m-%d %H:%M:%S")

        # If this is a row not of activity of interest
        if not act_mask[index]:
            # Log the previous activity, if present
            if cur_activity is not "":
                # Compute the number of hours
                cur_act_timedelta = cur_act_time - cur_starttime
                cur_act_timehours = (cur_act_timedelta /
                                     datetime.timedelta(hours=1))

                # Append to work dictionary (need to match WORK_DF_COLS)
                work_dict['Date'].append(file_date)
                work_dict['Weekday'].append(file_date.weekday() + 1)
                work_dict['Activity'].append(cur_activity)
                work_dict['StartTime'].append(cur_starttime)
                work_dict['DurationHours'].append(cur_act_timehours)
            continue

        # If this is an intermediate row of a multi-row activity
        if index > 0 and act_mask[index - 1]:
            cur_activity += f'|{row["Activity"]}'
            continue

        # If this is the first row of an activity - initialize activity
        if act_mask[index]:
            cur_starttime = cur_act_time
            cur_activity = row["Activity"]

    # ==
    # Initialize DataFrame and return
    cur_file_work_df = pd.DataFrame.from_dict(work_dict)
    return cur_file_work_df


def filter_wanted_activity(df: pd.DataFrame, col_name='Label',
                           label_include=2, label_gap=1) -> List[bool]:
    """
    Given a log filter DataFrame, filter (by activity type) for only the record
    (indexes) that specify the type of activity we are interested in

    :param df: The input df to be filtered
    :param col_name: the column name of the Label column
    :param label_include: the type of activity we are interested in
    :param label_gap: the type of activity that can be a part of the activity
                      we are interested in. (i.e. type 2 work with type 1 work
                      in between still counts as type 2 work over that whole
                      duration)
    :return: a boolean mask over the df indexes about which activities are of
             the type (label_include) we are interested in
    """

    # Get the activity types
    lab_list = df[col_name]

    # Initiate boolean mask
    lab_mask = [False] * len(lab_list)

    # Iterate over the label list
    for act_idx in range(len(lab_list)):
        # If the current activity is not the type we want then skip
        if lab_list[act_idx] != label_include:
            continue

        # If the activity is wanted, mark the mask as True
        lab_mask[act_idx] = True

        # Also check if the previous activity is a "gap" activity
        if (act_idx >= 2 and
                lab_list[act_idx - 1] == label_gap and
                lab_list[act_idx - 2] == label_include):
            lab_mask[act_idx - 1] = True

    return lab_mask


def main(args: argparse.Namespace) -> None:
    """Main method for feature extraction"""

    # ==
    # Format the date ranges
    date_ranges = args.date_range.split(':')
    if len(date_ranges) == 2:
        date_ranges = tuple([datetime.datetime.strptime(
            ele, "%Y-%m-%d").date() for ele in date_ranges])
    else:
        date_ranges = None

    # ==
    # Get a list of files to read
    file_dict = get_file_list(args.in_dir, date_ranges)

    # ==
    # Read the list of files and extract features from each
    work_df = read_extract_files(file_dict)

    # ==
    # Save the DataFrame
    if args.out_path.endswith('.pkl'):
        print(f'Pickling file to: {args.out_path}')
        work_df.to_pickle(args.out_path)
    else:
        print(work_df)


if __name__ == '__main__':
    # ==
    # Arguments
    parser = argparse.ArgumentParser(description='Productivity logs')

    parser.add_argument('--in-dir', type=str, required=True,
                        metavar='./path/to/input/directory',
                        help="""Path to the input directory containing
                                labelled logs""")
    parser.add_argument('--date-range', type=str, default='2019-01-01:2019-05-01',
                        metavar='yyyy-mm-dd:yyyy-mm-dd',
                        help="Date ranges to extract, -1 for all records")
    parser.add_argument('--out-path', type=str, default='None',
                        metavar='./path/to/out/file',
                        help="Path to save the output DataFrame, None for no save")

    args = parser.parse_args()
    print(args)

    main(args)
