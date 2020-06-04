# ===========================================================================
# Classifier to label / categorize logs
#
# Activity types, for reference only:
#   0: general-purpose not working
#   1: light work, organizing things, etc.
#   2: intensive work, concentrated with no distraction
#   -1: chilling and wasting time
#
# ===========================================================================
import csv
import glob
import os

from tqdm import tqdm

# (Input) Path to directory containing raw log data
RAW_LOG_DIR_PATH = 'INPUT_RAW_DIR/daily_logs'

# (Output) Path to directory containing labelled log data
LABELLED_LOG_DIR_PATH = 'OUTPUT_LABELLED_DIR/labelled_logs'

# (Reference only, not used)
# Label category mapping {index is array index - label name}
LABELS = {-1: 'chill', 0: 'not working', 1: 'light work', 2: 'intensive work'}

# (Input) Column index which contains the activity (count from 0)
ACTIVITY_COL_IDX = 2
# (Output) Column index which contains the label value
LABELIDX_COL_IDX = 3


# ===
def checkRawFileLabelled(raw_file_path: str) -> bool:
    """
    Function that checks if a log file is correctly manually labelled
    I.e. the "activities" column should start with "[z]" (z replaceable by
    a positive or negative integer)

    :param raw_file_path: the file path string of the log file I would like
                          to evaluate
    :return: true if the file is correctly manually labelled
    """
    # Read current raw file and skip header
    tsvRawFile = open(raw_file_path)
    tsvRawReader = csv.reader(tsvRawFile, delimiter='\t')
    inHeader = next(tsvRawReader, None)

    # Iterate through rows to check for validity
    for row in tsvRawReader:
        try:
            # Check for starting square bracket
            if row[ACTIVITY_COL_IDX][0] != '[':
                return False

            # Find the right (end) square bracket
            right_brac_idx = row[ACTIVITY_COL_IDX].find(']')

            # Check that the in between string is a valid integer
            int(row[ACTIVITY_COL_IDX][1:right_brac_idx])

        except:
            return False

    return True


# ===
def classifyLabelledRawFile(raw_file_path: str,
                            out_labelled_file_path: str) -> None:
    """
    Function that classifies a manually labelled raw log file

    :param raw_file_path: file path string of the (raw) input file to read
    :param out_labelled_file_path: file path string of the output (labelled)
                                   file to write to
    :return: None
    """
    # Read current raw file and skip header
    tsvRawFile = open(raw_file_path)
    tsvRawReader = csv.reader(tsvRawFile, delimiter='\t')
    inHeader = next(tsvRawReader, None)

    # Open output file and write header
    tsvOutFile = open(out_labelled_file_path, 'w')
    tsvWriter = csv.writer(tsvOutFile, delimiter='\t')
    outHeader = inHeader + ["Label"]
    tsvWriter.writerow(outHeader)

    # Read through and automatically label data
    for row in tsvRawReader:
        # Get the label index
        right_brac_idx = row[ACTIVITY_COL_IDX].find(']')
        labIdx = int(row[ACTIVITY_COL_IDX][1:right_brac_idx])

        # Take away the label from the activity string
        activityString = row[ACTIVITY_COL_IDX][right_brac_idx+1:]
        activityString = activityString.strip()
        row[ACTIVITY_COL_IDX] = activityString

        #Write to output file
        outRow = row + [labIdx]
        tsvWriter.writerow(outRow)

    tsvRawFile.close()
    tsvOutFile.close()



# ===
def main() -> None:
    """
    Main method to run the script
    """

    # Figure out the path to the processed and raw files
    raw_filePaths = glob.glob(os.path.join(RAW_LOG_DIR_PATH, '*.tsv'))
    lab_filePaths = glob.glob(os.path.join(LABELLED_LOG_DIR_PATH, '*.tsv'))

    #Keeping track of which labelled files are read
    readLabelledFilePaths = set([])

    # Keep track of which files are labelled
    print("Loading previously labelled files... ")
    for labFilePath in tqdm(lab_filePaths):
        readLabelledFilePaths.add(labFilePath)

    # Metrics output
    print('Number of previously labelled files: %d' % len(readLabelledFilePaths))
    print("\nStarting label encoding...")
    print('Total number of files: %d' % len(raw_filePaths))

    # Read the raw files, automatically classify
    numLabelled = 0
    for rawFilePath in tqdm(raw_filePaths):
        # Create final labelled log file name
        labFileName = "labelled_" + rawFilePath.split('/')[-1]
        labFilePath = os.path.join(LABELLED_LOG_DIR_PATH,labFileName)
        # Skip this raw file if it has previously been labelled
        if labFilePath in readLabelledFilePaths:
            continue

        # Check the raw file is correctly formatted
        if checkRawFileLabelled(rawFilePath) is True:
            # Label the files
            classifyLabelledRawFile(rawFilePath, labFilePath)
            numLabelled += 1

        # Record read label path
        readLabelledFilePaths.add(labFilePath)

    # Final metric
    print('New files labelled: %d' % numLabelled)

# Run this
main()
