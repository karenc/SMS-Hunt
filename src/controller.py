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
            'started': bool(hunt.started),
            'clues': clues,
            'clues_json': json.dumps([{
                'id': clue.key().id(),
                'question': clue.question,
                'answer': clue.answer
                } for clue in clues]),
            }))

    @utils.logged_in
    def post(self, hunt_id):
        def get_clues_list():
            '''Parses and validates the clues-list JSON'''
            try:
                clues_list = json.loads(self.request.get('clues-list'))
            except ValueError:
                print 'json parsing failed'
                return None
            if not isinstance(clues_list, list):
                print 'clues_list is not a list'
                return None
            for clue_dict in clues_list:
                if not isinstance(clue_dict, dict):
                    print 'clue_dict is not a dict'
                    return None
                for field in 'question', 'answer':
                    if field not in clue_dict:
                        print 'field missing from clue_dict'
                        return None
                    if not isinstance(clue_dict[field], basestring):
                        print 'field in clue_dict not a string'
                        return None
            return clues_list

        hunt = get_hunt_by_id(hunt_id)
        if not hunt:
            self.redirect('/')
            return
        clues_list = get_clues_list()
        if not clues_list:
            self.redirect('/')
            return
        if hunt.started:
            # TODO update existing clues
            pass
        else:
            for clue in Clue.all().filter('hunt =', hunt):
                clue.delete()

            for clue_dict in clues_list:
                Clue(hunt=hunt, question=clue_dict['question'], answer=clue_dict['answer']).put()
        self.redirect('/hunt/%s/clues' % hunt.key().id())
