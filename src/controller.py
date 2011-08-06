import json

from google.appengine.ext import webapp
from Hunt import Hunt

import utils

class Index(webapp.RequestHandler):
    @utils.logged_in
    def get(self):
        self.response.out.write(utils.render('templates/index.html', {}))


class CreateHunt(webapp.RequestHandler):
    @utils.logged_in
    def post(self):
        hunt_name = self.request.get('hunt-name')
        hunt = Hunt.all().filter('name =', hunt_name).get()
        if not hunt:
            hunt = Hunt(name=hunt_name)
            hunt.put()
        self.redirect('/hunt/%s' % hunt.key().id())


class ShowHunt(webapp.RequestHandler):
    @utils.logged_in
    def get(self, hunt_id):
        try:
            hunt_id = int(hunt_id)
        except ValueError:
            self.redirect('/')
            return
        hunt = Hunt.get_by_id(hunt_id)
        if not hunt:
            self.redirect('/')
            return
        self.response.out.write('Hunt Name: %s' % hunt.name)


class Clues(webapp.RequestHandler):
    @utils.logged_in
    def get(self, hunt_name):
        self.response.out.write(utils.render('templates/clues.html', {
            'hunt_name': hunt_name,
            'clues': json.dumps([{
                'id': '1',
                'clue': 'Clue 1',
                'answer': 'Answer 1'
                }]),
            }))
