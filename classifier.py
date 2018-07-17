# ===========================================================================
# Classifier to label / categorize logs
#
# ===========================================================================
import os, glob
import csv, subprocess
import numpy as np
import ProdLogUtils as PlUtils

#Path to directory containing raw log data
RAW_LOG_DIR_PATH = '/Users/anthony/Google_Drive/Life_Related/daily_logs'
#Path to directory containing labelled log data
LABELLED_LOG_DIR_PATH = '/Users/anthony/Google_Drive/Git_Projects/ProductivityLog/labelled_logs'

#Label category mapping {index - label name}
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
#Dictionary that keeps track of the word frequencies for each category
wordFreqDictionary = {}
#How many categories are there?
N_categories = len(LABELS)

# ===
# Function that reads a file into the word frequency dictionary
# ===
def readLabelledFile_2_wordFreqDict(lablled_file_path):
    #Open file and skip header
    tsvFile = open(lablled_file_path)
    tsvReader = csv.reader(tsvFile, delimiter='\t')
    next(tsvReader, None)

    #Read through file and save labelled data
    for row in tsvReader:
        sentFeatures = PlUtils.extract_sentence_feature(row[ACTIVITY_COL_IDX])
        sentLabelIdx = int(row[LABELIDX_COL_IDX])

        global wordFreqDictionary
        wordFreqDictionary = PlUtils.aggregate_word_freq(wordFreqDictionary, sentFeatures, sentLabelIdx, N_categories)

    #Close file and record read path
    tsvFile.close()

# ===
# Function that classifies a raw log file
# ===
def classifyRawFile(raw_file_path, out_labelled_file_path):
    #Read current raw file and skip header
    tsvRawFile = open(raw_file_path)
    tsvRawReader = csv.reader(tsvRawFile, delimiter='\t')
    inHeader = next(tsvRawReader, None)

    #Open output file and write header
    print('Opening file for output at: ' + out_labelled_file_path)
    tsvOutFile = open(out_labelled_file_path, 'w')
    tsvWriter = csv.writer(tsvOutFile, delimiter='\t')
    outHeader = inHeader + ["Label"]
    tsvWriter.writerow(outHeader)
    print(outHeader)

    #Read through and automatically label data
    for row in tsvRawReader:
        #Extraact feature and label data
        sentFeatures = PlUtils.extract_sentence_feature(row[ACTIVITY_COL_IDX])
        labProbs = PlUtils.naiveBayesianClassifier(wordFreqDictionary, sentFeatures, N_categories)
        maxProbLabIdx = np.argmax(labProbs) #Get most likely label

        #Write to output file
        outRow = row + [maxProbLabIdx]
        tsvWriter.writerow(outRow)
        print(outRow + [LABELS[maxProbLabIdx]])

    tsvRawFile.close()
    tsvOutFile.close()



# ===
# Script starts
# ===

#Read all the labelled data to generate a work frequency bank (prior knowledge)
for labFilePath in lab_filePaths:
    readLabelledFile_2_wordFreqDict(labFilePath)
    readLabelledFilePaths.add(labFilePath)


#Read the raw files, automatically classify and indicate to user
for rawFilePath in raw_filePaths:
    #Create labelled log file name
    labFileName = "labelled_" + rawFilePath.split('/')[-1]
    labFilePath = os.path.join(LABELLED_LOG_DIR_PATH,labFileName)
    #Skip if the labelled file is already created, skip
    if labFilePath in readLabelledFilePaths:
        continue

    #Automatically classify file and write
    classifyRawFile(rawFilePath, labFilePath)
    #TODO: use a intermediate temp file instaed?
    #TODO overall idea is don't create the final labelled file unless i confirm it is correct
    #TODO: July 15, this is the next step, as well as more testing to make sure it works

    #Check if the label are correct, if not, manually fix
    keyboard_in = input('Labels correct? [y/n]: ')
    if keyboard_in != 'y':
        print('Opening file')
        p = subprocess.Popen(['open',labFilePath, '-a', 'Microsoft Excel']) #mac-specific
        p.wait()
        input('Press any keys to continue...')
    print('\n')

    #Add newly created labels to the dictionary!
    readLabelledFile_2_wordFreqDict(labFilePath)

    #Record read label path
    readLabelledFilePaths.add(labFilePath)

    #break #TODO temp