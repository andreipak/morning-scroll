import sys
from termcolor import colored

class NewsChunk(object):

    def __init__(self, entry, language):
        self.entry = entry
        self.weight = 0
        self.hitnames = []
        self.language = language

    def getTitle(self):
        return self.entry["title"]

    def getEntry(self):
        return self.entry

    def getHitnames(self):
        return self.hitnames

    def getWeight(self):
        return self.weight

    def getLanguage(self):
        return self.language

    # hits are dictionaries, but what is added are hitnames
    def addHit(self, hit):
        if type(hit) is dict:
            self.hitnames.append(hit["title"])
            self.weight += hit["weight"]
        else:
            print("something")
            return

    def worthShowing(self):
        showWeight = 3

        if self.weight >= showWeight:
            return True
        else:
            return False

    def print_info(self):

        importantColor = "red"
        hitColor = "yellow"
        weightColor = "green"
        
        if self.getWeight() > 0:
            sys.stdout.write(colored("     [", weightColor))
            sys.stdout.write(colored(str(self.getWeight()), weightColor))
            sys.stdout.write(colored("] ", weightColor))

        if self.worthShowing():
            sys.stdout.write(colored(self.getTitle(), importantColor))
        elif self.getWeight() > 0:
            sys.stdout.write(self.getTitle())
        else:
            sys.stdout.write("\t" + self.getTitle())

        if self.getWeight() > 0:
            sys.stdout.write(colored(" ( ", hitColor))
            for hitname in self.getHitnames():
                sys.stdout.write(colored(hitname.upper(), hitColor))
                sys.stdout.write(colored(" ", hitColor))
            sys.stdout.write(colored(")", hitColor))
        print
