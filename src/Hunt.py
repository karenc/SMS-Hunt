from google.appengine.ext import db
from google.appengine.api import users
import random
from datetime import datetime

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

    def finished_teams(self):
        """Returns all teams that have finished."""
        return filter(lambda t: t.finished(), self.teams)

    def outstanding_teams(self):
        """Returns all teams that have not finished yet."""
        return filter(lambda t: not t.finished(), self.teams)

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
    finish_time = db.DateTimeProperty()

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
        return self.clues()[0] if self.clues() else None

    def guess(self, answer):
        """Guess the answer to the current clue. If wrong, returns
        False. If right, removes the clue from self.clues(), stores a
        Success object and returns True."""
        c = self.current_clue()
        if answer.lower() == c.answer.lower():
            s = Success(hunt=self.hunt, team=self, clue=c)
            s.put()
            self._remove_clue()
            return True
        else:
            return False

    def finished(self):
        """Returns a boolean to say if team has finished or not."""
        return not self.clue_keys

    def pass_clue(self):
        """Quit the current clue permanently in order not to get
        stuck. No Success object is added."""
        self._remove_clue()
        return True

    def _remove_clue(self):
        """Internal method used by answer and pass_clue"""
        self.clue_keys.pop(0)
        if self.finished():
            self.finish_time = datetime.now()
        self.put()
        return True

class Success(db.Model):
    """Every time a team gets the answer right, a Success is stored"""

    hunt = db.ReferenceProperty(Hunt, collection_name='successes')
    team = db.ReferenceProperty(Team, collection_name='successes')
    clue = db.ReferenceProperty(Clue)
    time = db.DateTimeProperty(auto_now_add=True)
