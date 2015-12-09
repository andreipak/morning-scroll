# Datascraper.py

# This file schedules constant query of feeds.
# Reads the hitlists and feeds to save the relevant entries to datastore

import feedparser # parse rss feeds from news sites
import json # read local hitlist datafiles

import difflib # determine duplicate-like articles
from newschunks import NewsChunks # datastore model containing entry, weight, and
                                  # title
from google.appengine.ext import db

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
PATH_TO_METALISTS = "metalists/"

# some constants, will be part of the object declaration
feednames_src = PATH_TO_METALISTS + "en_feednames"
hitlistnames_src = PATH_TO_METALISTS + "en_hitlistnames"

# threshold for difflib calculation
# 0.44 seems to catch most things, could be improved by weighting our hit-terms
# more
DUPLICATE_THRESHOLD = 0.44

def get_list_of(names_src):
    names = []
    with open(names_src) as f:
        names.extend(f.read().splitlines())
    return names

def get_hitlist_dict(hitlistnames_src):
    # initialize object data
    hitlist_dict = {}
    hitlistnames = get_list_of(hitlistnames_src)

    # Load hitlists from the names
    for hitlistname in hitlistnames:
        logging.debug(hitlistname)
        with open(PATH_TO_HITLISTS + hitlistname + HITLIST_EXTENSION) as data_file:
            tmp = json.load(data_file)
            hitlist_dict[hitlistname] = tmp[hitlistname]
            # this model exists for better weight algorithm in the future
    return hitlist_dict

def get_entries(url):
    try:
        rss = feedparser.parse(url)
        logging.debug(rss.feed.title + ": Loading...")
    except Exception as e:
        logging.debug(str(e))
    return rss.entries

# Loads the feeds onto the local (plan: language is either "kr" or "en")
def load_newschunks(entries, hitlist_dict):
    for new_entry in entries:
        new_title = new_entry.title

        match_nc = None

        q = db.Query(NewsChunks,keys_only=True)

        for key in q:
            existing_title = str(key)
            logging.debug(existing_title)
            # checks for duplicates with sequence matcher
            ratio = difflib.SequenceMatcher(None, new_title, existing_title).ratio()
            if ratio > DUPLICATE_THRESHOLD:
                match_nc = NewsChunks.get(existing_title)
                break

        # serializes entry into entry_data
        new_nc = NewsChunks(key_name=new_title, entry_data=pickle.dumps(new_entry))

        for hitlistname in hitlist_dict:
            for hit in hitlist_dict[hitlistname]:
                if hit["title"] in new_title.lower(): # it's a hit!
                    new_nc.hitnames.append(hit["title"])
                    new_nc.weight += hit["weight"]

        if match_nc is None:
            # unique nc
            new_nc.put()
        elif new_nc.weight > match_nc.weight:
            # similar, but new_nc is heavier
            match_nc.delete()
            new_nc.put()

# load all the feeds, then clear newschunks
def fetch(feednames_src, hitlistnames_src):
    feednames = get_list_of(feednames_src)
    for url in feednames:
        entries = get_entries(url)
        hitlist_dict = get_hitlist_dict(hitlistnames_src)
        load_newschunks(entries, hitlist_dict)
        logging.debug("Done")

def generate_feed(min_weight=3):
    items = []
    for nc in NewsChunks.all():

        # must be added for quality results!
        if nc.weight < min_weight:
            continue

        x = pickle.loads(nc.entry_data)
        items.append(PyRSS2Gen.RSSItem(
            title = x.title,
            link = x.link,
            description = x.summary,
            guid = x.link,
            pubDate = x.published
        ))

    # feed generation!
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

    return rss.to_xml(encoding="utf-8")

if __name__ == '__main__':
    main()
