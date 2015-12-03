import sys

class NewsChunk(object):

    def __init__(self, entry):
        self.entry = entry
        self.weight = 0
        self.hitnames = []

    def getTitle(self):
        if type(self.entry) is dict:
            return self.entry["title"]
        return None

    def getEntry(self):
        return self.entry

    def getHitnames(self):
        return self.hitnames

    def getWeight(self):
        return self.weight

    # hits are dictionaries, but what is added are hitnames
    def addHit(self, hit):
        if type(hit) is dict:
            self.hitnames.append(hit["title"])
            self.weight += hit["weight"]
        else:
            print("something")
            return
