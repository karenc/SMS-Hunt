from google.appengine.ext import webapp
from Hunt import Hunt

h = Hunt(name="Test hunt")
h.put()
h.add_clue("The hotel's name", "Mint")
h.add_clue("Leeds ____?", "Hack")

print "Content-Type: text/plain\n"

print "Hunt test!\n"
print "Hunt name: %s\n" % h.name

for c in h.clues:
    print "Clue %d:" % c.key().id()
    print "Question: %s" % c.question
    print "Answer: %s" % c.answer
    print ""

