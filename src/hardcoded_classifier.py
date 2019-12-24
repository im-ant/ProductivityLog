# ===========================================================================
# Classifier to label / categorize logs
#
# ===========================================================================
import os, glob
import csv, subprocess
import numpy as np
import ProdLogUtils as PlUtils

#Path to directory containing raw log data
RAW_LOG_DIR_PATH = '/Users/anthony/Google_Drive/Life_Ideas/daily_logs'
#Path to directory containing labelled log data
LABELLED_LOG_DIR_PATH = '/Users/anthony/Google_Drive/Git_Projects/ProductivityLog/labelled_logs'

#Name of the temporary file generated during auto-classification
TEMP_LAB_FILE_NAME = "tempLabelledFile_randomNum31415926.tsv"

#Label category mapping {index is array index - label name}
LABELS = ['not working', 'light work', 'intensive work']

#Column index which contains the activity (count from 0)
ACTIVITY_COL_IDX = 2
#Column index which contains the label value
LABELIDX_COL_IDX = 3

#Figure out the path to the processed and raw files
raw_filePaths = glob.glob(os.path.join(RAW_LOG_DIR_PATH, '*.tsv'))
lab_filePaths = glob.glob(os.path.join(LABELLED_LOG_DIR_PATH, '*.tsv'))

#Keeping track of which labelled files are read
readLabelledFilePaths = set([])

#How many categories are there?
N_categories = len(LABELS)


# ===
# Function that checks if a log file is correctly manually labelled
# I.e. the "activities" column should start with [0] (0 replaceable by
# an integer)
# ===
def checkRawFileLabelled(raw_file_path):
    # Read current raw file and skip header
    tsvRawFile = open(raw_file_path)
    tsvRawReader = csv.reader(tsvRawFile, delimiter='\t')
    inHeader = next(tsvRawReader, None)

    # Variable to keep track of this this file is properly labelled
    isLabelled = True

    # Iterate through rows to check for validity
    for row in tsvRawReader:
        try:
            # Check for square brackets
            if row[ACTIVITY_COL_IDX][0] != '[':
                return False
            if row[ACTIVITY_COL_IDX][2] != ']':
                return False

            # Check for label integer
            int(row[ACTIVITY_COL_IDX][1])
        except:
            return False

    return True


# ===
# Function that classifies a manually labelled raw log file
# ===
def classifyLabelledRawFile(raw_file_path, out_labelled_file_path):
    # Read current raw file and skip header
    tsvRawFile = open(raw_file_path)
    tsvRawReader = csv.reader(tsvRawFile, delimiter='\t')
    inHeader = next(tsvRawReader, None)

    # Open output file and write header
    tsvOutFile = open(out_labelled_file_path, 'w')
    tsvWriter = csv.writer(tsvOutFile, delimiter='\t')
    outHeader = inHeader + ["Label"]
    tsvWriter.writerow(outHeader)

    #Read through and automatically label data
    for row in tsvRawReader:
        # Get the label index from the hard-coding
        labIdx = int(row[ACTIVITY_COL_IDX][1])

        # Take away the label from the activity string
        activityString = row[ACTIVITY_COL_IDX][3:]
        activityString = activityString.strip()
        row[ACTIVITY_COL_IDX] = activityString


        #Write to output file
        outRow = row + [labIdx]
        tsvWriter.writerow(outRow)

    tsvRawFile.close()
    tsvOutFile.close()



# ===
# Script starts
# ===

# Keep track of which files are labelled
print("Loading previously labelled files... ")
for labFilePath in lab_filePaths:
    readLabelledFilePaths.add(labFilePath)

# Metrics output
print('Number of previously labelled files: %d' % len(readLabelledFilePaths))
print("\nStarting label encoding...")
print('Total number of files: %d' % len(raw_filePaths))

# Read the raw files, automatically classify
numLabelled = 0
for rawFilePath in raw_filePaths:
    # Create final labelled log file name
    labFileName = "labelled_" + rawFilePath.split('/')[-1]
    labFilePath = os.path.join(LABELLED_LOG_DIR_PATH,labFileName)
    # Skip this raw file if it has previously been labelled
    if labFilePath in readLabelledFilePaths:
        continue

    # Check the raw file is correctly labelled
    if checkRawFileLabelled(rawFilePath) is True:
        classifyLabelledRawFile(rawFilePath, labFilePath)
        numLabelled += 1

    # Record read label path
    readLabelledFilePaths.add(labFilePath)

# Final metric
print('New files labelled: %d' % numLabelled)
