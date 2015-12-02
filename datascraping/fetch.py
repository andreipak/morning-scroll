import sys
import feedparser
import json
from collections import defaultdict

feedlist = ["http://techcrunch.com/feed/"]

filternames = ["competitors",
             "korea",
             "business"]
data_of = defaultdict(list)
PATH_TO_DATA = ""
DATA_EXTENSION = ".json"

entries_list = []
entries_rejects = []

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
                unique = False
                break
        if unique:
            entries_list.append(entry)
    print(d.feed.title + ": Load Complete")

# Returns true if entry is valid according to the filters
def valid(entry):
    for fn in filternames:
        for filt in data_of[fn]:
            if filt["word"] in entry.title.lower():
                # print("I found "+filt["word"]+" in "+entry.title)
                return True
    return False

# Displays the entries in a savvy manner
def display(entries):
    for entry in entries:
        print("\t" + entry.title)

# Fetch stuff
def main():
    init()
    # feedlist = read_feedlist("feedlist.txt")
    for url in feedlist:
        load_entries(url)
    display(entries_list)
    print("\nAnd now... \n")
    valid_entries_list = filter(valid, entries_list)
    display(valid_entries_list)
    print("\n\t200")
    # return entries_list

if __name__ == '__main__':
    main()
