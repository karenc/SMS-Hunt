from google.appengine.ext import db
from google.appengine.api import users
import random
from datetime import datetime
import logging
import SMS
import re

class Hunt(db.Model):
    """Parent object of each treasure hunt"""

    owner = db.UserProperty()
    name = db.StringProperty()
    started = db.DateTimeProperty()
    
    def add_clue(self,q,a):
        """Add a new clue to this hunt."""
        c = Clue(hunt=self,question=q,answer=a)
        c.put()
        return c

    def add_team(self,n,p):
        """Add a new team to this hunt."""
        # Check if there's a team already with this number - if so,
        # null its phone number.
        old = Team.find_by_phone(p)
        if old:
            logging.warn("Found old team in hunt '%s' with this number. Blanking number!" % old.hunt.name)
            old.phone = None
            old.put()
        t = Team(hunt=self,name=n,phone=p,clue_keys=[])
        t.put()
        return t

    def start(self):
        """Start the hunt! Set up the clues and send the first clue to
        each team."""
        self.started = datetime.now()
        self.put()
        self.setup_clues()
        for t in self.teams:
            logging.debug("Clues for team %s: %s" % (t.name, [c.question for c in t.clues()]))
            t.send_clue('First clue: ')

    def setup_clues(self):
        """Adds all clues to each team in a random order."""
        for t in self.teams:
            t._reset_clues()

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

    @classmethod
    def find_by_phone(cls, p):
        """Class method to find a team by phone number. There should
        only be one... otherwise bad things happen!"""
        ts = cls.all().filter('phone =', p).fetch(1)
        return ts[0] if ts else None

    @classmethod
    def deliver(cls, p, msg):
        """Given a phone number and a message, deliver the message to
        the appropriate team's read_message() method."""
        logging.debug("Asked to deliver '%s' to %s" % (msg, p))
        team = cls.find_by_phone(p)
        logging.debug("Found team: %s" % team.name)
        if team:
            return team.read_message(msg)
        else:
            # Er... message received from unknown number
            return SMS.send(p, "Sorry... I don't know who you are!")

    def _reset_clues(self):
        """Populate clue_keys with a shuffled list of keys for the current clues. Should not be called publicly - use hunt.setup_clues()"""
        cids = [c.key().id() for c in self.hunt.clues]
        random.shuffle(cids)
        self.clue_keys = cids
        self.put()

    def clues(self):
        """Clue objects remaining to be answered by this team."""
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
            if self.clue_keys:
                self.send_clue("Awesome! Next: ")
            return True
        else:
            SMS.send(self.phone, "Sorry; that's wrong!")
            return False

    def finished(self):
        """Returns a boolean to say if team has finished or not."""
        return not self.clue_keys

    def score(self):
        """Returns the number of successes this team has had."""
        s = list(self.successes)
        return len(s)

    def remaining(self):
        """Returns the number of clues this team has left to
        solve. May not be total - finished because of passes."""
        c = list(self.clue_keys)
        return len(c)

    def has_clue_left(self, c):
        """Returns true if team has given clue left to answer."""
        return c.key().id() in self.clue_keys

    def correctly_answered(self, c):
        """Returns true if team correctly answered given clue."""
        return bool(Success.all().filter('team =', self).filter('clue =', c).fetch(1))

    def pass_clue(self):
        """Quit the current clue permanently in order not to get
        stuck. No Success object is added."""
        self._remove_clue()
        if self.clue_keys:
            self.send_clue("Aww too bad! Next: ")
        return True

    def send_clue(self, note=''):
        """Send the current clue to the team by SMS, prepended by note."""
        msg = note
        if self.current_clue():
            msg += self.current_clue().question
        else:
            msg += 'No more clues!'
        result = SMS.send(self.phone, msg)
        return True if result == 200 else False

    def read_message(self, msg):
        """Process an incoming text for this team. 'pass' or '<answer>'"""
        if re.search('^\s*pass\s*$', msg, re.I):
            return self.pass_clue()
        return self.guess(msg)

    def _remove_clue(self):
        """Internal method used by answer and pass_clue"""
        self.clue_keys.pop(0)
        if self.finished():
            self.finish_time = datetime.now()
            result = SMS.send(self.phone, "You're finished! Return to base.")
        self.put()
        return True

class Success(db.Model):
    """Every time a team gets the answer right, a Success is stored"""

    hunt = db.ReferenceProperty(Hunt, collection_name='successes')
    team = db.ReferenceProperty(Team, collection_name='successes')
    clue = db.ReferenceProperty(Clue)
    time = db.DateTimeProperty(auto_now_add=True)
