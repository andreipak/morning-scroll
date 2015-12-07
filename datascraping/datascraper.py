import sys
import libs.feedparser.feedparser
import json # for reading json files
from collections import defaultdict # for initialization
from libs.termcolor import colored # for savvy debugging
import libs.schedule # for scheduled stuff
import time
from newschunk import NewsChunk
import difflib # for getting rid of duplicate-like articles
import datetime
import libs.PyRSS2Gen # for generating feed

feednames_src = "metalists/en_feednames"
hitlistnames_src = "metalists/en_hitlistnames"
PATH_TO_DATA = "hitlists/"
DATA_EXTENSION = ".json"
# 0.44 seems to catch most things, could be improved by weighting our hit-terms
# more
DUPLICATE_THRESHOLD = 0.44

PRINT_ALL = False
def print_info(newschunks):
    if len(newschunks) <= 0:
        return
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

class DataScraper(object):

    def __init__(self):
        self.feednames = []
        self.hitlistnames = []
        self.data_of = defaultdict(list)

        # archive_newschunks has everything, and newschunks has the recent stuff
        self.newschunks = {}
        self.archive_newschunks = {}

        # Loads the filters onto the self.data_of dictionary
        with open(PATH_TO_DATA + feednames_src) as f:
            self.feednames.extend(f.read().splitlines())

        with open(PATH_TO_DATA + hitlistnames_src) as f:
            self.hitlistnames.extend(f.read().splitlines())

        for hitlistname in self.hitlistnames:
            print(hitlistname)
            with open(PATH_TO_DATA + hitlistname + DATA_EXTENSION) as data_file:
                tmp = json.load(data_file)
                self.data_of[hitlistname] = tmp[hitlistname]
                # data_of is now a proper dictionary of list of dictionaries!
                # Valid use would be 'data_of[filtername][index]["title"]'
                # or for competitors, 'data_of[filtername][index]["tier"]' works too!
        print

    def add_nc(self, new_nc):
        self.newschunks[new_nc.getTitle()] = new_nc
        self.archive_newschunks[new_nc.getTitle()] = new_nc

    # deletes a newschunk from the dictionary (also deletes the key)
    def del_nc(self, old_nc):
        # del the original
        if old_nc is not None:
            self.newschunks.pop(old_nc.getTitle())
            self.archive_newschunks.pop(old_nc.getTitle())
        else:
            print("ERROR: Could not delete properly")

    # Loads the feeds onto the newschunks (language is either "kr" or "en")
    def load_newschunks(self, url):
        d = libs.feedparser.feedparser.parse(url)
        for entry in d.entries:
            ratio = 0
            match_nc = None
            for existing_title in self.archive_newschunks:
                # checks for duplicates with sequence matcher
                # quick_ratio is an option if it gets too slow, but really fetching
                # is the bottleneck
                ratio = difflib.SequenceMatcher(None, entry.title, existing_title).ratio()
                if ratio > DUPLICATE_THRESHOLD:
                    # if ratio < 1.0:
                    #     print(entry.title)
                    #     print(existing_title)
                    #     print(ratio)
                    match_nc = self.archive_newschunks[existing_title]
                    break

            new_nc = NewsChunk(entry)
            for fn in self.data_of:
                for hit in self.data_of[fn]:
                    if hit["title"] in entry.title.lower(): # it's a hit!
                        new_nc.addHit(hit)

            if match_nc is None:
                self.add_nc(new_nc)
            elif new_nc.getWeight() > match_nc.getWeight():
                # similar, but more important
                self.del_nc(match_nc)
                self.add_nc(new_nc)

        print(d.feed.title + ": Load Complete")


    # Fetch stuff
    def fetch(self):
        # feedlist = read_feedlist("feedlist.txt")
        for url in self.feednames:
            self.load_newschunks(url)
        print
        print
        # print_info(self.newschunks)
        # newschunks show what to print during scheduling
        self.newschunks.clear()
        print("\t200")
        print

    def generate_feed(self):
        items = []
        for title in self.archive_newschunks:
            nc = self.archive_newschunks[title]
            # if not nc.worthShowing():
            #     continue
            x = nc.getEntry()
            items.append(libs.PyRSS2Gen.RSSItem(
                title = x.title,
                link = x.link,
                description = x.summary,
                guid = x.link,
                pubDate = x.published
            ))

        rss = libs.PyRSS2Gen.RSS2(
                title = "The Feed, yo",
                link = "https://morning-scroll.appspot.com",
                description = "This is a feed",

                language = "en",
                copyright = "",
                pubDate = datetime.datetime.now(),
                lastBuildDate = datetime.datetime.now(),

                categories = "",
                generator = "",
                docs = "https://validator.w3.org/feed/docs/rss2.html",

                items = items
        )

        return rss.to_xml()

    def schedule_fetch(self):
        libs.schedule.every(10).minutes.do(self.fetch)
        while 1:
            libs.schedule.run_pending()
            time.sleep(1)

    if __name__ == '__main__':
        main()
