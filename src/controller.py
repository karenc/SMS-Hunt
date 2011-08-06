import json

from google.appengine.ext import webapp
from Hunt import Hunt, Clue

import utils

def get_hunt_by_id(hunt_id):
    '''Fetch the hunt given an id string'''
    try:
        hunt_id = int(hunt_id)
    except ValueError:
        return None
    return Hunt.get_by_id(hunt_id)

class Index(webapp.RequestHandler):
    @utils.logged_in
    def get(self):
        hunts = list(Hunt.all().filter('owner =', self.user))
        self.response.out.write(utils.render('templates/index.html', {'hunts': hunts}))


class CreateHunt(webapp.RequestHandler):
    @utils.logged_in
    def post(self):
        hunt_name = self.request.get('hunt-name')
        hunt = Hunt.all().filter('name =', hunt_name).get()
        if not hunt:
            hunt = Hunt(name=hunt_name, owner=self.user)
            hunt.put()
        self.redirect('/hunt/%s' % hunt.key().id())


class ShowHunt(webapp.RequestHandler):
    @utils.logged_in
    def get(self, hunt_id):
        hunt = get_hunt_by_id(hunt_id)
        if not hunt:
            self.redirect('/')
            return
        self.response.out.write('Hunt Name: %s' % hunt.name)


class Clues(webapp.RequestHandler):
    @utils.logged_in
    def get(self, hunt_id):
        hunt = get_hunt_by_id(hunt_id)
        if not hunt:
            self.redirect('/')
            return
        clues = list(Clue.all().filter('hunt =', hunt))
        self.response.out.write(utils.render('templates/clues.html', {
            'hunt_name': hunt.name,
            'clues': json.dumps([{
                'id': clue.key().id(),
                'question': clue.question,
                'answer': clue.answer
                } for clue in clues]),
            }))
