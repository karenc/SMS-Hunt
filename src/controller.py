import json

from google.appengine.ext import webapp
from Hunt import Hunt, Clue, Team

import utils

def get_hunt_by_id(hunt_id):
    '''Fetch the hunt given an id string'''
    try:
        hunt_id = int(hunt_id)
    except ValueError:
        return None
    return Hunt.get_by_id(hunt_id)

def parse_json_objs(objs, fields):
    '''Parse and validate a JSON object list'''
    try:
        objs = json.loads(objs)
    except ValueError:
        print 'json parsing failed'
        return None
    if not isinstance(objs, list):
        print 'objs is not a list'
        return None
    for obj in objs:
        if not isinstance(obj, dict):
            print 'obj is not a dict'
            return None
        for field in fields:
            if field not in obj:
                print 'field missing from obj'
                return None
            if not isinstance(obj[field], basestring):
                print 'field in obj not a string'
                return None
    return objs


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
        hunt = get_hunt_by_id(hunt_id)
        if not hunt:
            self.redirect('/')
            return
        clues_list = parse_json_objs(self.request.get('clues-list'), ['question', 'answer'])
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


class Teams(webapp.RequestHandler):
    @utils.logged_in
    def get(self, hunt_id):
        hunt = get_hunt_by_id(hunt_id)
        if not hunt:
            self.redirect('/')
            return
        teams = list(Team.all().filter('hunt = ', hunt))
        self.response.out.write(utils.render('templates/teams.html', {
            'hunt_name': hunt.name,
            'started': bool(hunt.started),
            'teams': teams,
            'teams_json': json.dumps([{
                'id': team.key().id(),
                'name': team.name,
                'phone': team.phone,
                } for team in teams]),
            }))
