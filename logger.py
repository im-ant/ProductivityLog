#!/usr/bin/python3.6
###############################################################################
# Script that stays on a generate a .tsv file of self-logged daily activities,
# mainly with the goal of keeping myself accountable to my work hours.
#
# All you have to do is run it and write to the command line the activity you
# are doing / starting when you start it and it will create a log.
###############################################################################

import os, csv, time, datetime

### Path of the daily log file ###
OUTPUT_FILE = "/YOUR_CUSTOM_PATH_TO_DIRECTORY/%s_log.tsv" % datetime.datetime.now().strftime("%Y-%m-%d")

### Open output stream and csv writer ###
if not os.path.isfile(OUTPUT_FILE):
    print("Writing new file to: %s\n" % OUTPUT_FILE)
    outFile = open(OUTPUT_FILE,'w')
    outFile_writer = csv.writer(outFile, delimiter='\t', lineterminator='\n')
    outFile_writer.writerow(['Date','Time', 'Activity'])
else:
    print("Opening existing file at: %s\n" % OUTPUT_FILE)
    outFile = open(OUTPUT_FILE,'a')
    outFile_writer = csv.writer(outFile, delimiter='\t', lineterminator='\n')


### Iterate indefinitely ###
while(True):
    #Try to get user input
    try:
        keyboard_in = input('Enter activity: ')
    #If the user ctrl+C, clear line
    except KeyboardInterrupt:
        print("")
        continue
    #If the user ctrl+D, terminate the program
    except EOFError:
        break

    #Get the current date and time
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    time_str = datetime.datetime.now().strftime("%H:%M:%S")

    #Let the user know what he wrote
    print("%s\t%s\n" % (time_str, keyboard_in))

    #Write to the excel file
    outFile_writer.writerow([date_str, time_str, keyboard_in])

    #Wait a bit for suspense
    time.sleep(0.2)


### Indicate user and Close stream ###
print("\n\nLogger Halted. Closing file: %s" % OUTPUT_FILE)
outFile.close()
