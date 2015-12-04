import sys
from termcolor import colored

class NewsChunk(object):

    def __init__(self, entry):
        self.entry = entry
        self.weight = 0
        self.hitnames = []

    def getTitle(self):
        return self.entry["title"]

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

    showWeight = 3
    def worthShowing(self):
        if self.weight >= 3:
            return True
        else:
            return False

    def print_info(self):
        if self.getWeight() > 0:
            sys.stdout.write(colored("     [", "green"))
            sys.stdout.write(colored(str(self.getWeight()), "green"))
            sys.stdout.write(colored("] ", "green"))

        if self.worthShowing():
            sys.stdout.write(colored(self.getTitle(), "red"))
        elif self.getWeight() > 0:
            sys.stdout.write(self.getTitle())
        else:
            sys.stdout.write("\t" + self.getTitle())

        if self.getWeight() > 0:
            sys.stdout.write(colored(" ( ", "grey"))
            for hitname in self.getHitnames():
                sys.stdout.write(colored(hitname.upper(), "grey"))
                sys.stdout.write(colored(" ", "grey"))
            sys.stdout.write(colored(")", "grey"))
        print
