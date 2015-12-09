# Datascraper.py

# This file schedules constant query of feeds.
# Reads the hitlists and feeds to save the relevant entries to datastore

import feedparser # parse rss feeds from news sites
import json # read local hitlist datafiles

import difflib # determine duplicate-like articles
from newschunk import NewsChunk # datastore model containing entry, weight, and
                                # title
import pickle # serialize (write to datastore) & deserialize (generate feed)
              # individual entries

import schedule # schedule fetches
import time # adjunct to schedule

import PyRSS2Gen # generate feed
from datetime import datetime # publish current time for rss feed generation

import logging # debugging

# some constants regarding directories
PATH_TO_HITLISTS = "hitlists/"
HITLIST_EXTENSION = ".json"
PATH_TO_METALISTS = PATH_TO_HITLISTS + "metalists/"

# some constants, will be part of the object declaration
feednames_src = "en_feednames"
hitlistnames_src = "en_hitlistnames"

# threshold for difflib calculation
# 0.44 seems to catch most things, could be improved by weighting our hit-terms
# more
DUPLICATE_THRESHOLD = 0.44

class DataScraper(object):

    def __init__(self):
        # initialize object data
        self.feednames = []
        self.hitlistnames = []
        self.data_of = {}

        # this should also be datastored !!
        self.archive_newschunks = {}

        # Load feed names
        with open(PATH_TO_METALISTS + feednames_src) as f:
            self.feednames.extend(f.read().splitlines())

        # Load hitlist names
        with open(PATH_TO_METALISTS + hitlistnames_src) as f:
            self.hitlistnames.extend(f.read().splitlines())

        # Load hitlists from the names
        for hitlistname in self.hitlistnames:
            logging.debug(hitlistname)
            with open(PATH_TO_HITLISTS + hitlistname + HITLIST_EXTENSION) as data_file:
                tmp = json.load(data_file)
                self.data_of[hitlistname] = tmp[hitlistname]
                # data_of is now a dictionary of list of newschunks
                # this model exists for better weight algorithm in the future

    # Loads the feeds onto the local (plan: language is either "kr" or "en")
    def load_newschunks(self, url):
        d = feedparser.parse(url)
        for new_entry in d.entries:
            new_title = new_entry.title

            match_title = ""
            match_nc = None

            for existing_title in self.archive_newschunks:
                # checks for duplicates with sequence matcher
                ratio = difflib.SequenceMatcher(None, new_title, existing_title).ratio()
                if ratio > DUPLICATE_THRESHOLD:
                    match_title = existing_title
                    match_nc = self.archive_newschunks[match_title]
                    break

            # serializes entry into entry_data
            new_nc = NewsChunk(entry_data=pickle.dumps(new_entry))

            for fn in self.data_of:
                for hit in self.data_of[fn]:
                    if hit["title"] in new_title.lower(): # it's a hit!
                        new_nc.hitnames.append(hit["title"])
                        new_nc.weight += hit["weight"]

            if match_nc is None:
                # unique nc
                self.archive_newschunks[new_title] = new_nc
            elif new_nc.weight > match_nc.weight:
                # similar, but new_nc is heavier
                self.archive_newschunks.pop(match_title)
                self.archive_newschunks[new_title] = new_nc

        logging.debug(d.feed.title + ": Load Complete")

    # load all the feeds, then clear newschunks
    def fetch(self):
        for url in self.feednames:
            self.load_newschunks(url)
        logging.debug("\t200")

    def generate_feed(self):
        items = []
        for title in self.archive_newschunks:
            nc = self.archive_newschunks[title]
            # must be added for quality results!
            # if nc.weight < 3:
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
