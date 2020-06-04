# ============================================================
# Bash script to quickly get a summary of the past 3 weeks
# ============================================================

# ==
# Set up

# Set up paths
base_path="path_to_base_directory"
script_path="$base_path/src/feature_extract.py"
lab_dir_path="$base_path/labelled_logs/"

# Set up date range
start_date=$(date -v-21d '+%Y-%m-%d')
end_date=$(date '+%Y-%m-%d')
date_range="$start_date:$end_date"

# ==
# Run

echo "Date range: $date_range"

python $script_path --in-dir=$lab_dir_path \
                    --date-range=$date_range
