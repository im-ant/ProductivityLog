# ProductivityLog
Things to help analyze workflow and productive hours.

### Dependencies

- Python 3
- `tqdm` (pretty progress bars)
- `pandas`
- `matplotlib` (for plots)
- `seaborn` (for pretty plots)



## Usage example

#### S1: Logging
**S1.1**
Each day before you start work, enter:
```sh
python src/logger.py
```

This generates the **log file** with path `OUTPUT_FILE`. The path can be modified [here](https://github.com/im-ant/ProductivityLog/blob/d37b8961a5b2c976a3f4349d8fd3fe03a10c1daa/src/logger.py#L13).


**S1.2**
The above will start the script and initialize the file. Simply type into the terminal the current activity and it will be recorded, along with the date and time. An example terminal screen with one activity entered:

```txt
Writing new file to: /Users/anthony/Google_Drive/Life_Ideas/daily_logs/2020-06-04_log.tsv

Enter activity: [2] working on coding up productivity tools
10:02:10	    [2] working on coding up productivity tools

Enter activity:
```

**S1.3**
After you are done, simply press `ctrl+D` to exit. You can also use `ctrl+C` aytime to cancel the current "entry loop" (behind the hood it is just an infinite for loop, each loop waits for the user to enter data).


**S1.appendix**
A side note is that I use different numbering schemes to categorize the "intensity" of work. This can be specified by simplying entering a number in square brackets (`[?]`) before entering the activity. I use the following numbering scheme (but you do not have to follow it):

| Number  | Work type                                                   |
| --------|:-----------------------------------------------------------:|
| `[0]`   | miscellaneous activites, not really work, taking breaks     |
| `[1]`   | light work, working with distractions, multi-tasking, things that do not contribute to a longer-term goal, etc.  |
| `[2]`   | deep work in an enviroment with no distractions             |
| `[-1]`  | very meaningless activities (e.g. mindless web surfing)     |


#### S2: Activity labelling

**S2.1**
After the **log file** has been generated, we organize it by categorizing its activity to generate the **labelled files** directory. The below script just uses the manually specified labels (see table above):

```sh
python src/hardcoded_classifier.py
```

Where `RAW_LOG_DIR_PATH` specifies where directory containing **log file** is, and the labelled `.tsv` files are written to `LABELLED_LOG_DIR_PATH`. See [hardcoded_classifier.py](https://github.com/im-ant/ProductivityLog/blob/master/src/hardcoded_classifier.py) for more details.


**S2.appendix**
You can also use fancier methods to classify things (e.g. Naive Bayes classifier using word frequency [here](https://github.com/im-ant/ProductivityLog/blob/master/src/classifier.py)), but I opted for simplicity in the end.


#### S3: Analyzing activity

You can run whatever analysis on your logged activites. Personally, I run the following:

**S3.1**
```sh
python src/feature_extract.py --in-dir path/to/labelled/files/dir \
                              --date-range 2020-06-01:2020-06-04
```

which generates a table and plot summarizing the number of deep work (`[2]`) and "meaningless" (`[-1]`) hours each day for the days inside of `--date-range`.

The output table will look something like:
```
          Date  Weekday  WorkHours_Max  WorkHours_Sum  WasteHours_Sum
0   2020-05-14        4       2.507222       4.321944        0.960278
1   2020-05-15        5       2.355278       3.803889        3.524722
2   2020-05-16        6       0.948056       0.948056        8.493611
3   2020-05-17        7       1.400000       1.937778        0.374167
4   2020-05-18        1       3.585278       4.934722        3.652222
```

In fact, you can also specify `--out-path`, which saves a `pandas.DataFrame` object for further analysis / visualization.

**S3.appendix**
To make things easier, I also have a `.sh` script to do the above quickly:
```sh
bash src/quick_summary.sh
```
which does the same thing but with the `--in-dir` hard-coded and `--date-range` set to the past 3 weeks from today.







## Scripts and Functionalities
(**Outdated section**)

#### logger.py
Script used to self-report activities. After initializing via command line, the user can type in what he/she is doing currently, which will be logged with the date and time. Each productivity log file is in a .tsv format and a single file contains the activities of a given day.

#### ProdLogUtils.py
Utilities to help with the classifications. Has functions which pre-processes a sentence into tokens, aggregates the word frequency dictionary to generate prior distributions and does the classification.

#### classifier.py
(*Deprecated*)
Script that is ran to classify log files. Uses previously classified log files as a knowledge bank to classify new files. Currently the classifier is a naive bayesian classifier using word frequencies associated with each categories of labels.
