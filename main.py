#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import sys
reload(sys)
# sys.setdefaultencoding("utf-8")
import webapp2
import cgi
import feedparser
import datascraper
import logging
from google.appengine.ext import db
from google.appengine.api import mail
from newschunks import NewsChunks

# some constants regarding directories
PATH_TO_HITLISTS = "hitlists/"
HITLIST_EXTENSION = ".json"
PATH_TO_METALISTS = "metalists/"
KOREAN = True
ENGLISH = False

def fetch(IS_KOREAN):
    if IS_KOREAN:
        datascraper.fetch(PATH_TO_METALISTS + "kr_feednames",
                PATH_TO_METALISTS + "kr_hitlistnames_general",
                PATH_TO_METALISTS + "kr_hitlistnames_exclusive")
    else:
        datascraper.fetch(PATH_TO_METALISTS + "en_feednames", 
                PATH_TO_METALISTS + "en_hitlistnames_general",
                PATH_TO_METALISTS + "en_hitlistnames_exclusive")

class MailHandler(webapp2.RequestHandler):
    def get(self):
        mail.send_mail("joshchonpc@gmail.com", "joshchonpc@gmail.com", "Week Whatever", datascraper.generate_html(3, 20))

class DBClearHandler(webapp2.RequestHandler):
    def get(self):
        db.delete(NewsChunks.all())

class FetchHandler(webapp2.RequestHandler):
    def get(self):
        fetch(KOREAN)
        fetch(ENGLISH)

MINWEIGHT = 3

class RSSHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/rss+xml'
        self.response.write(datascraper.generate_feed(MINWEIGHT))

class DebugHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write(datascraper.generate_html(2, 3))

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write(datascraper.generate_html(3, 15))
        # self.response.headers['Content-Type'] = 'application/rss+xml'
        # self.response.write("\t\t\t\t\t==============IMPORTANT==============\n")
        # self.response.write(datascraper.generate_human_readable_feed(3, 10))
        # self.response.write("\n\t\t\t\t\t===========ALMOST IMPORTANT===========\n")
        # self.response.write(datascraper.generate_human_readable_feed(2, 3))
        # self.response.write("\n\t\t\t\t\t============NOT IMPORTANT============\n")
        # self.response.write(datascraper.generate_human_readable_feed(1, 2))

app = webapp2.WSGIApplication([
    ('/', MainHandler), ('/debug', DebugHandler), ('/rss', RSSHandler), ('/tasks/mail', MailHandler), ('/tasks/dbclear', DBClearHandler), ('/tasks/fetch', FetchHandler)
], debug=True)
