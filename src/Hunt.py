from google.appengine.ext import db
from google.appengine.api import users

class Hunt(db.Model):
    """Parent object of each treasure hunt"""

    owner = db.UserProperty()
    name = db.StringProperty()
    
    def add_clue(self,q,a):
        """Add a new clue to this hunt."""
        c = Clue(hunt=self,question=q,answer=a)
        c.put()

class Clue(db.Model):
    """Each treasure hunt has multiple clues, each with a question and
    an answer."""

    hunt     = db.ReferenceProperty(Hunt, collection_name='clues')
    question = db.StringProperty()
    answer   = db.StringProperty()

