# NewsChunk is a datastore Model from Google App Engine
# entry_data (blob) : pickle-serialized version of entry_data
# weight (int)      : weight of the entry
# hitnames (list)   : hits that contributed to the weight
from google.appengine.ext import db

class NewsChunks(db.Model):
<<<<<<< HEAD
    entry_data = db.BlobProperty(required = True)
    weight     = db.IntegerProperty(default = 0)
    hitnames   = db.ListProperty(str)
    title      = db.StringProperty(required = True)
=======
    entry_data = db.BlobProperty(required=True)
    weight = db.IntegerProperty(default=0)
    hitnames = db.ListProperty(str)
<<<<<<< HEAD
<<<<<<< HEAD
>>>>>>> parent of 8270007... version 3.0 english algorithm optimized
=======
>>>>>>> parent of 8270007... version 3.0 english algorithm optimized
=======
>>>>>>> parent of 8270007... version 3.0 english algorithm optimized
