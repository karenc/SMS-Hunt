from google.appengine.ext import db
from google.appengine.api import users
import random

class Hunt(db.Model):
    """Parent object of each treasure hunt"""

    owner = db.UserProperty()
    name = db.StringProperty()
    
    def add_clue(self,q,a):
        """Add a new clue to this hunt."""
        c = Clue(hunt=self,question=q,answer=a)
        c.put()
        return c

    def add_team(self,n,p):
        """Add a new team to this hunt."""
        t = Team(hunt=self,name=n,phone=p,clue_keys=[])
        t.put()
        return t

class Clue(db.Model):
    """Each treasure hunt has multiple clues, each with a question and
    an answer."""

    hunt     = db.ReferenceProperty(Hunt, collection_name='clues')
    question = db.StringProperty()
    answer   = db.StringProperty()

class Team(db.Model):
    """A team searching for answers to a given hunt."""
    
    hunt     = db.ReferenceProperty(Hunt, collection_name='teams')
    name     = db.StringProperty()
    phone    = db.StringProperty()

    # This is the full list of remaining clues for this team. Populate
    # initially with reset_clues
    clue_keys    = db.ListProperty(int, default=[])

    def reset_clues(self):
        """Populate clue_keys with a shuffled list of keys for the current clues"""
        cids = [c.key().id() for c in self.hunt.clues]
        random.shuffle(cids)
        self.clue_keys = cids
        self.put()

    def clues(self):
        return [Clue.get_by_id(id) for id in self.clue_keys]

    def current_clue(self):
        """Get the current clue this team must solve"""
        return self.clues()[0]
