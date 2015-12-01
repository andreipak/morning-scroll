import sys
import feedparser
import json
from collections import defaultdict

feedlist = ["http://techcrunch.com/feed/"]

filternames = ["competitors"]#,
             # "korea",
             # "business"]
data_of = defaultdict(dict)
DATA_EXTENSION = ".json"

entries_list = []
entries_rejects = []

# Loads the filters onto the data_of dictionary
def init():
    for filtername in filternames:
        with open(filtername + DATA_EXTENSION) as data_file:
            print(filtername)
            dummy = json.load(data_file)
            data_of = dummy[filtername]
            dumb = data_of[filtername][1]
            print(dumb['word'])

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
    for filtername in filternames:
        for term in data_of[filtername]:
            if term in entry.title.lower():
                print("I found "+term+" in "+entry.title)
                return True
    return False

# Displays the entries in a savvy manner
def display(entries):
    for entry in entries:
        print("\t" + entry.title)

def main():
    init();
    # feedlist = read_feedlist("feedlist.txt")
    for url in feedlist:
        load_entries(url)
    display(entries_list)
    print("\nAnd now... \n")
    valid_entries_list = filter(valid, entries_list)
    display(valid_entries_list)
    print("\n\t200")

# Boilerplate
if __name__ == '__main__':
    main()
