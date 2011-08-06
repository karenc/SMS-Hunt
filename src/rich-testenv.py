from google.appengine.ext import webapp
from Hunt import *

# Create a hunt
h = Hunt(name="Test hunt")
h.put()

# Add some clues to the hunt
h.add_clue("Chair colour", "purple")
h.add_clue("Hotel name", "Mint")
h.add_clue("#leeds____?", "hack")
h.add_clue("Rich's Twitter name", "pedantic_git")

# Add some teams
h.add_team("Foo", "071234567").reset_clues()
h.add_team("Bar", "072345678").reset_clues()
h.add_team("Baz", "073456789").reset_clues()

def print_clues(hunt):
    for t in hunt.teams:
        print "Team: %s" % t.name
        print "Clues in order:"
        for c in t.clues():
            print "  - %s" % c.question
        print ""
        print "Current clue: %s" % t.current_clue().question
        print ""

print "Content-Type: text/plain\n"

print "Hunt test!\n"
print "Hunt name: %s\n" % h.name

print_clues(h)

for t in h.teams:
    print "%s guesses 'PURPLE'" % t.name
    result = t.guess("PURPLE")
    print "Correct!" if result else "Wrong!"
    print ""

print_clues(h)

for s in h.successes:
    print "Success: %s for clue '%s' at %s" % (s.team.name, s.clue.question, s.time)
