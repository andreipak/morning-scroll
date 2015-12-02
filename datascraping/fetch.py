import sys
import feedparser # for parsing feeds
import json # for reading json files
from collections import defaultdict # for initialization
from termcolor import colored # for savvy debugging
import schedule # for scheduled stuff
import time

feedlist = ["http://techcrunch.com/feed/"]

# otherwise known as validators
filternames = [# "competitors",
             # "korea",
             "business"]#,
             # "industry"]
data_of = defaultdict(list)
PATH_TO_DATA = ""
DATA_EXTENSION = ".json"

entries_list = []
entries_weight = []

DEBUG = False

# Loads the filters onto the data_of dictionary
def init():
    for filtername in filternames:
        with open(PATH_TO_DATA + filtername + DATA_EXTENSION) as data_file:
            tmp = json.load(data_file)
            data_of[filtername] = tmp[filtername]
            # data_of is now a proper dictionary of list of dictionaries!
            # Valid use would be 'data_of[filtername][index]["word"]'
            # or for competitors, 'data_of[filtername][index]["tier"]' works too!
        if DEBUG:
            for fn in filternames:
                for entry in data_of[fn]:
                    print entry["word"]

# Loads the feeds onto the entries_list
def load_entries(url):
    d = feedparser.parse(url)
    for entry in d.entries:
        unique = True
        for existing_entry in entries_list:
            if existing_entry.title == entry.title:
                # no duplicates allowed
                unique = False
                break
        if unique:
            entries_list.append(entry)
            # entries_weight[entry.title][
    print(d.feed.title + ": Load Complete")

# Returns true if entry is valid according to the filters
def valid(entry):
    for fn in filternames:
        for filt in data_of[fn]:
            if filt["word"] in entry.title.lower(): # checks on lower case
                sys.stdout.write(colored("\t" + entry.title, "green"))
                print(" [" + filt["word"].upper() + "]")
                print
                return True
    print("\t" + entry.title)
    print
    return False

# Displays the entries in a savvy manner
def display(entries):
    for entry in entries:
        print("\t" + entry.title)

# Fetch stuff
def fetch():
    # feedlist = read_feedlist("feedlist.txt")
    for url in feedlist:
        load_entries(url)
    valid_entries_list = filter(valid, entries_list)
    print("\t200")
    # return entries_list

def main():
    init()
    print("initiation complete")
    fetch();
    schedule.every().minutes.do(fetch)
    while 1:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main()
