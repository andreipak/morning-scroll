from newschunk import NewsChunk

s = {"title": "Superman"}
d = {"title": "Batman"}
s_newschunk = NewsChunk(s, 3)
d_newschunk = NewsChunk(d, 4)

print(s_newschunk.getTitle())
print(s_newschunk.getEntry())
print(s_newschunk.getWeight())

print(d_newschunk.getTitle())
print(s_newschunk.sumWeightWith(d_newschunk))
