# morning-scroll

Morning Scroll is a simple rss news aggregator/synthesizer. The program uses
feedparser to get the news, filters the entries using an algorithm on the
title, and synthesizes a new rss feed in the form of a webpage, email, or rss
feed. News is aggregated over the course of a week, archived by a simple
email, then database is wiped.

Used Google App Engine, fetchparser.py, PyRSS2Gen.py, W3.css, and schedule.py.

Things to work on:

- Algorithm Optimization/Robust Testing
- Better Documentation
- NAVER OpenAPI      (better sources)
- Security           (fetch does not lock the database)
- Feed Customization (make editing user-friendly)
- Threading          (will make fetch much faster)
- Native Support     (email, Responsive Web, etc.)
- Crunchbase Tooltip (upon hover display information about company)
