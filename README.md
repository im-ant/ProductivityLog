# ProductivityLog
Things to help analyze workflow and productive hours.

### Dependencies:
- Python 3
- Numpy
- nltk


## Scripts and Functionalities
#### logger.py
Script used to self-report activities. After initializing via command line, the user can type in what he/she is doing currently, which will be logged with the date and time. Each productivity log file is in a .tsv format and a single file contains the activities of a given day.

#### ProdLogUtils.py
Utilities to help with the classifications. Has functions which pre-processes a sentence into tokens, aggregates the word frequency dictionary to generate prior distributions and does the classification.

#### classifier.py
Script that is ran to classify log files. Uses previously classified log files as a knowledge bank to classify new files. Currently the classifier is a naive bayesian classifier using word frequencies associated with each categories of labels.
