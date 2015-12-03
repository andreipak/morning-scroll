import sys

class NewsChunk(object):

    def __init__(self, entry, weight):
        self.entry = entry
        self.weight = weight

    def getTitle(self):
        if type(self.entry) is dict:
            return self.entry["title"]
        return None

    def getEntry(self):
        return self.entry

    def getWeight(self):
        return self.weight

    def sumWeightWith(self, otherNewsChunk):
        if type(otherNewsChunk) is NewsChunk:
            return self.getWeight() + otherNewsChunk.getWeight()
