# NewsChunk is a datastore Model from Google App Engine
# entry_data (blob) : pickle-serialized version of entry_data
# weight (int)      : weight of the entry
# hitnames (list)   : hits that contributed to the weight
from google.appengine.ext import db

class NewsChunks(db.Model):
    entry_data = db.BlobProperty(required=True)
    weight = db.IntegerProperty(default=0)
    hitnames = db.ListProperty(str)
