import sys
import webapp2
import feedparser
import simplejson
import json
from collections import defaultdict # for initialization
from termcolor import colored # for savvy debugging
import schedule # for scheduled stuff
import time
from newschunk import NewsChunk
import difflib # for getting rid of duplicate-like articles
from datetime import datetime
import PyRSS2Gen # for generating feed
from google.appengine.ext import db
import logging
import pickle

feednames_src = "metalists/en_feednames"
hitlistnames_src = "metalists/en_hitlistnames"
PATH_TO_DATA = "hitlists/"
DATA_EXTENSION = ".json"
# 0.44 seems to catch most things, could be improved by weighting our hit-terms
# more
DUPLICATE_THRESHOLD = 0.44

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

    def add_nc(self, new_nc, title):
        self.newschunks[title] = new_nc
        self.archive_newschunks[title] = new_nc

    # deletes a duplicate newschunk from the dictionary (also deletes the key)
    def del_nc(self, old_nc, title):
        # del the original
        if old_nc is not None:
            self.newschunks.pop(title)
            self.archive_newschunks.pop(title)

    # Loads the feeds onto the newschunks (language is either "kr" or "en")
    def load_newschunks(self, url):
        d = feedparser.parse(url)
        for entry in d.entries:
            ratio = 0
            match_nc = None
            for existing_title in self.archive_newschunks:
                # checks for duplicates with sequence matcher
                # quick_ratio is an option if it gets too slow, but really fetching
                # is the bottleneck
                ratio = difflib.SequenceMatcher(None, entry.title, existing_title).ratio()
                if ratio > DUPLICATE_THRESHOLD:
                    match_nc = self.archive_newschunks[existing_title]
                    break

            new_nc = NewsChunk(title=entry.title, entry_data=pickle.dumps(entry))
            for fn in self.data_of:
                for hit in self.data_of[fn]:
                    if hit["title"] in entry.title.lower(): # it's a hit!
                        new_nc.hitnames.append(hit["title"])
                        new_nc.weight += hit["weight"]

            if match_nc is None:
                self.add_nc(new_nc, entry.title)
            elif new_nc.weight > match_nc.weight:
                # similar, but more important
                self.del_nc(match_nc, entry.title)
                self.add_nc(new_nc, entry.title)

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
            x = pickle.loads(nc.entry_data)
            items.append(PyRSS2Gen.RSSItem(
                title = x.title,
                link = x.link,
                description = x.summary,
                guid = x.link,
                pubDate = x.published
            ))

        rss = PyRSS2Gen.RSS2(
                title = "The Feed, y",
                link = "https://morning-scroll.appspot.com",
                description = "This is a feed",

                language = "en",
                copyright = "",
                pubDate = datetime.now(),
                lastBuildDate = datetime.now(),

                categories = "",
                generator = "",
                docs = "https://validator.w3.org/feed/docs/rss2.html",

                items = items
        )

        return rss.to_xml()

    def schedule_fetch(self):
        schedule.every(10).minutes.do(self.fetch)
        while 1:
            schedule.run_pending()
            time.sleep(1)

    if __name__ == '__main__':
        main()
