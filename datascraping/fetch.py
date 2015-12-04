import sys
import feedparser # for parsing feeds
import json # for reading json files
from collections import defaultdict # for initialization
from termcolor import colored # for savvy debugging
import schedule # for scheduled stuff
import time
from newschunk import NewsChunk
import difflib # for getting rid of duplicate-like articles

feedlist = ["http://newssearch.naver.com/search.naver?where=rss&query=%B9%E8%B4%DE+%BE%DB&field=0",
"http://techcrunch.com/feed/"]#, "http://mashable.com/feed",
        # "https://venturebeat.com/feed/"]

# otherwise known as validators
filternames = ["kr_competitors",
             "competitors",
             "korea",
             "business",
             "industry"]
data_of = defaultdict(list)
PATH_TO_DATA = ""
DATA_EXTENSION = ".json"

# archive_newschunks has everything, and newschunks has the recent stuff
newschunks = {}
archive_newschunks = {}

# Loads the filters onto the data_of dictionary
def init():
    for filtername in filternames:
        with open(PATH_TO_DATA + filtername + DATA_EXTENSION) as data_file:
            tmp = json.load(data_file)
            data_of[filtername] = tmp[filtername]
            # data_of is now a proper dictionary of list of dictionaries!
            # Valid use would be 'data_of[filtername][index]["title"]'
            # or for competitors, 'data_of[filtername][index]["tier"]' works too!

# 0.44 seems to catch most things, could be improved by weighting our hit-terms
# more
DUPLICATE_THRESHOLD = 0.44

# Loads the feeds onto the newschunks
def load_newschunks(url):
    d = feedparser.parse(url)
    for entry in d.entries:
        ratio = 0
        unique = True
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
                unique = False
                break
        if unique:
            print(ratio)
            new_nc = NewsChunk(entry)
            for fn in filternames:
                for hit in data_of[fn]:
                    if hit["title"] in entry.title.lower(): # it's a hit!
                        new_nc.addHit(hit)
            newschunks[entry.title] = new_nc
            archive_newschunks[entry.title] = new_nc
    print(d.feed.title + ": Load Complete")

def print_newschunks():
    for title in newschunks:
        nc = newschunks[title]
        if nc.getWeight() < 3:
            sys.stdout.write("\t" + title)
        else:
            sys.stdout.write(colored("\t" + title, "red"))

        if nc.getWeight() > 0:
            sys.stdout.write(colored(" [ ", "green"))
            for hitname in nc.getHitnames():
                sys.stdout.write(colored(hitname.upper(), "green"))
                sys.stdout.write(colored(" ", "green"))
            sys.stdout.write(colored("]", "green"))
            sys.stdout.write(colored(" [score: "+str(nc.getWeight())+"]", "green"))
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
    for url in feedlist:
        load_newschunks(url)
    print_newschunks()
    # newschunks show what to print during scheduling
    newschunks.clear()
    print("\t200")

def main():
    init()
    print("initiation complete")
    fetch()
    fetch()
    # schedule.every().minutes.do(fetch)
    # while 1:
    #     schedule.run_pending()
    #     time.sleep(1)

if __name__ == '__main__':
    main()
