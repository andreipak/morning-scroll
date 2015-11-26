import sys
import feedparser

feedlist = ["https://www.google.com/alerts/feeds/03016667448555882041/10813419956796523147",
            "https://www.google.com/alerts/feeds/03016667448555882041/18371980089906002277",
            "https://www.google.com/alerts/feeds/03016667448555882041/1720301016679370235"]

# def read_feedlist(filename)

# def valid(entry)

def main(): 
    # feedlist = read_feedlist("feedlist.txt")
    for url in feedlist:
        d = feedparser.parse(url)
        print(d.feed.title)
        entries = filter(valid, d.entries)
        for entry in entries:
            print(entry.title)

# Boilerplate
if __name__ == '__main__':
    main()
