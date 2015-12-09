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

form="""
<!DOCTYPE html>

<html>
  <head>
    <title>Sign Up</title>
  </head>

  <body>
    <h2>Signup</h2>
    <form method="post">
        Quantity (between 0 and 5):
        <input type="number" name="minweight" min="0" max="5">
        <input type="submit">
    </form>
  </body>

</html>
"""

# some constants regarding directories
PATH_TO_HITLISTS = "hitlists/"
HITLIST_EXTENSION = ".json"
PATH_TO_METALISTS = "metalists/"
KOREAN = True
ENGLISH = False

def fetch(IS_KOREAN):
    if IS_KOREAN:
        datascraper.fetch(PATH_TO_METALISTS + "kr_feednames", PATH_TO_METALISTS + "kr_hitlistnames")
    else:
        datascraper.fetch(PATH_TO_METALISTS + "en_feednames", PATH_TO_METALISTS + "en_hitlistnames")

class FetchHandler(webapp2.RequestHandler):
    def get(self):
        fetch(KOREAN)
        fetch(ENGLISH)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(form)

    def post(self):
        minweight = self.request.get('minweight')
        self.redirect("/cgi-bin/feed2html.py?i=/generation?minweight=%s"%minweight)

class GenerationHandler(webapp2.RequestHandler):
    def get(self):
        minweight = self.request.get('minweight')
        self.response.write(datascraper.generate_feed(int(minweight)))

app = webapp2.WSGIApplication([
    ('/', MainHandler), ('/fetch', FetchHandler), ('/generation', GenerationHandler)
], debug=True)
