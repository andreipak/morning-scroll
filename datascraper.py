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

# threshold for difflib calculation
# 0.44 seems to catch most things, could be improved by weighting our hit-terms
# more
DUPLICATE_THRESHOLD = 0.6

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

# Loads the feeds onto the local (plan: language is either "kr" or "en")
def load_newschunks(entries, hitlist_general_dict, hitlist_exclusive_dict):
    for new_entry in entries:
        cond1 = isinstance(new_entry.title, basestring)
        cond2 = new_entry.title == ""
        if cond1 and cond2:
            continue
        else:
            new_title = new_entry.title

        new_nc = NewsChunks(title=new_title, entry_data=pickle.dumps(new_entry))

        for hitlistname in hitlist_general_dict:
            for hit in hitlist_general_dict[hitlistname]:
                if hit["title"].lower() in new_title.lower(): # it's a regular hit!
                    new_nc.hitnames.append(hit["title"])
                    new_nc.weight += hit["weight"]

        exclusive_hit_title = ""
        exclusive_hit_weight = 0
        for hitlistname in hitlist_exclusive_dict:
            for hit in hitlist_exclusive_dict[hitlistname]:
                if hit["title"].lower() in new_title.lower():
                    if hit["weight"] > exclusive_hit_weight: # it's an exclusive hit!
                        exclusive_hit_title = hit["title"]
                        exclusive_hit_weight = hit["weight"]
        if exclusive_hit_weight > 0:
            new_nc.hitnames.append(exclusive_hit_title)
            new_nc.weight += exclusive_hit_weight

        if new_nc.weight == 0:
            continue

        match_nc = None

        q = db.Query(NewsChunks)
        best_match_ratio = DUPLICATE_THRESHOLD
        for nc in q:
            existing_title = nc.title
            # checks for duplicates with sequence matcher
            ratio = difflib.SequenceMatcher(None, new_title, existing_title).ratio()
            if ratio > best_match_ratio:
                if nc.weight >= new_nc.weight:
                    return
                else:
                    best_match_ratio = ratio
                    match_nc = nc

        if match_nc is None:
            # unique nc
            new_nc.put()
        else:
            # similar, but new_nc is heavier
            match_nc.delete()
            new_nc.put()

# load all the feeds, then clear newschunks
def fetch(feednames_src, hitlistnames_general_src, hitlistnames_exclusive_src):
    feednames = get_list_of(feednames_src)
    hitlist_general_dict = get_hitlist_dict(hitlistnames_general_src)
    hitlist_exclusive_dict = get_hitlist_dict(hitlistnames_exclusive_src)
    for url in feednames:
        # try:
        try:
            rss = feedparser.parse(url)
        except Exception as e:
            continue
        load_newschunks(rss.entries, hitlist_general_dict, hitlist_exclusive_dict)
        try:
            logging.debug(rss.feed.title)
        except Exception as e:
            print
        logging.debug(" Done")
        # except Exception as e:
        #     logging.debug(e.message)

def generate_feed(min_weight=3):
    items = []
    q = db.Query(NewsChunks)
    for nc in q:

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

def generate_human_readable_feed(min_weight, max_weight):
    output = ""
    q = NewsChunks.all()
    q.filter("weight <", max_weight)
    q.filter("weight >=", min_weight)
    for nc in q:

        # must be added for quality results!
        x = pickle.loads(nc.entry_data)

        output += "\n\t" + nc.title + " ["
        for hitname in nc.hitnames:
            output += " " + hitname
        output += " ]\n"
        output += "\t"+x.link+"\n"

    return output

if __name__ == '__main__':
    main()
