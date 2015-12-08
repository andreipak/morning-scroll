# import sys
# from libs.termcolor import colored
# import datetime
from google.appengine.ext import db
from google.appengine.api import users

class NewsChunk(db.Model):
    entry_json = db.StringProperty(required=True)
    weight = db.IntegerProperty(default=0)
    hitnames = db.ListProperty(str)
    #
    # def __init__(self, entry):
    #     self.entry = entry
    #     self.weight = 0
    #     self.hitnames = []
    #
    # def getTitle(self):
    #     return self.entry["title"]
    #
    # def getEntry(self):
    #     return self.entry
    #
    # def getHitnames(self):
    #     return self.hitnames
    #
    # def getWeight(self):
    #     return self.weight
    #
    #
    # # hits are dictionaries, but what is added are hitnames
    # def addHit(self, hit):
    #     if type(hit) is dict:
    #         self.hitnames.append(hit["title"])
    #         self.weight += hit["weight"]
    #     else:
    #         print("something")
    #         return
    #
    # def worthShowing(self):
    #     showWeight = 3
    #
    #     if self.weight >= showWeight:
    #         return True
    #     else:
    #         return False
    #
    # def print_info(self):
    #
    #     importantColor = "red"
    #     hitColor = "yellow"
    #     weightColor = "green"
    #
    #     if self.getWeight() > 0:
    #         sys.stdout.write(colored("     [", weightColor))
    #         sys.stdout.write(colored(str(self.getWeight()), weightColor))
    #         sys.stdout.write(colored("] ", weightColor))
    #
    #     if self.worthShowing():
    #         sys.stdout.write(colored(self.getTitle(), importantColor))
    #     elif self.getWeight() > 0:
    #         sys.stdout.write(self.getTitle())
    #     else:
    #         sys.stdout.write("\t" + self.getTitle())
    #
    #     if self.getWeight() > 0:
    #         sys.stdout.write(colored(" ( ", hitColor))
    #         for hitname in self.getHitnames():
    #             sys.stdout.write(colored(hitname.upper(), hitColor))
    #             sys.stdout.write(colored(" ", hitColor))
    #         sys.stdout.write(colored(")", hitColor))
    #     print
