import sys
import feedparser # for parsing feeds
import json # for reading json files
from collections import defaultdict # for initialization
from termcolor import colored # for savvy debugging
import schedule # for scheduled stuff
import time
from newschunk import NewsChunk
import difflib # for getting rid of duplicate-like articles

feednames_src = "en_feednames"
feednames = []

hitlistnames_src = "en_hitlistnames"
hitlistnames = []

data_of = defaultdict(list)
PATH_TO_DATA = ""
DATA_EXTENSION = ".json"

# archive_newschunks has everything, and newschunks has the recent stuff
newschunks = {}
archive_newschunks = {}

# Loads the filters onto the data_of dictionary
def init():
    with open(feednames_src) as f:
        feednames.extend(f.read().splitlines())

    with open(hitlistnames_src) as f:
        hitlistnames.extend(f.read().splitlines())

    for hitlistname in hitlistnames:
        print(hitlistname)
        with open(PATH_TO_DATA + hitlistname + DATA_EXTENSION) as data_file:
            tmp = json.load(data_file)
            data_of[hitlistname] = tmp[hitlistname]
            # data_of is now a proper dictionary of list of dictionaries!
            # Valid use would be 'data_of[filtername][index]["title"]'
            # or for competitors, 'data_of[filtername][index]["tier"]' works too!
    print

# should make a class for newschunks...
def add_nc(new_nc):
    newschunks[new_nc.getTitle()] = new_nc
    archive_newschunks[new_nc.getTitle()] = new_nc

# deletes a newschunk from the dictionary (also deletes the key)
def del_nc(old_nc):
    # del the original
    if old_nc is not None:
        newschunks.pop(old_nc.getTitle())
        archive_newschunks.pop(old_nc.getTitle())
    else:
        print("ERROR: Could not delete properly")

# 0.44 seems to catch most things, could be improved by weighting our hit-terms
# more
DUPLICATE_THRESHOLD = 0.44

# Loads the feeds onto the newschunks (language is either "kr" or "en")
def load_newschunks(url):
    d = feedparser.parse(url)
    for entry in d.entries:
        ratio = 0
        match_nc = None
        for existing_title in archive_newschunks:
            # checks for duplicates with sequence matcher
            # quick_ratio is an option if it gets too slow, but really fetching
            # is the bottleneck
            ratio = difflib.SequenceMatcher(None, entry.title, existing_title).ratio()
            if ratio > DUPLICATE_THRESHOLD:
                # if ratio < 1.0:
                #     print(entry.title)
                #     print(existing_title)
                #     print(ratio)
                match_nc = archive_newschunks[existing_title]
                break

        new_nc = NewsChunk(entry)
        for fn in data_of:
            for hit in data_of[fn]:
                if hit["title"] in entry.title.lower(): # it's a hit!
                    new_nc.addHit(hit)

        if match_nc is None:
            add_nc(new_nc)
        elif new_nc.getWeight() > match_nc.getWeight():
            # similar, but more important
            del_nc(match_nc)
            add_nc(new_nc)

    print(d.feed.title + ": Load Complete")

PRINT_ALL = False
def print_info(newschunks):
    notImportant = []
    almostImportant = []
    important = []
    for title in newschunks:
        nc = newschunks[title]
        if nc.worthShowing():
            important.append(nc)
        elif nc.getWeight() > 0:
            almostImportant.append(nc)
        else:
            notImportant.append(nc)

    # sorts by weight
    almostImportant.sort(key=lambda x: x.getWeight(), reverse=False)
    important.sort(key=lambda x: x.getWeight(), reverse=False)

    if PRINT_ALL:
        # activate for algorithm optimization, floods the stuff a lot
        if len(notImportant) > 0:
            for nimp in notImportant:
                nimp.print_info()
            print
            print("\t---------------------------------------")
            print

    if len(almostImportant) > 0:
        for almostimp in almostImportant:
            almostimp.print_info()
        print
        print("\t---------------------------------------")
        print

    if len(important) > 0:
        for imp in important:
            imp.print_info()
        print
        print("\t---------------------------------------")
        print

# Returns true if entry is valid according to the filters
# def valid(entry):
#     for fn in filternames:
#         for filt in data_of[fn]:
#             if filt["title"] in entry.title.lower(): # checks on lower case
#                 sys.stdout.write(colored("\t" + entry.title, "green"))
#                 print(" [" + filt["title"].upper() + "]")
#                 print
#                 return True
#     print("\t" + entry.title)
#     print
#     return False

# Displays the entries in a savvy manner
# def display(entries):
#     for entry in entries:
#         print("\t" + entry.title)

# Fetch stuff
def fetch():
    # feedlist = read_feedlist("feedlist.txt")
    for url in feednames:
        load_newschunks(url)

    print

    if len(newschunks) > 0:
        print
        print_info(newschunks)
        # newschunks show what to print during scheduling
        newschunks.clear()

    print("\t200")
    print

def main():
    init()
    fetch()
    schedule.every(10).minutes.do(fetch)
    while 1:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main()
