from google.appengine.ext import webapp

import utils

class CreateHunt(webapp.RequestHandler):
    @utils.logged_in
    def post(self):
        hunt_name = self.request.get('hunt-name')
        self.redirect('/hunt/%s' % hunt_name)

class ShowHunt(webapp.RequestHandler):
    @utils.logged_in
    def get(self, name):
        self.response.out.write('Hunt Name: %s' % name)

class Clues(webapp.RequestHandler):
    @utils.logged_in
    def get(self, hunt_name):
        self.response.out.write(utils.render('templates/clues.html', {
            'hunt_name': hunt_name,
            }))
