import logging
import simplejson as json
import re

from google.appengine.ext import webapp

from Hunt import Hunt, Clue, Team
import utils

PHONE_NUMBER_RE = re.compile(r'^\d+$')

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
        logging.warning('json parsing failed')
        return None
    if not isinstance(objs, list):
        logging.warning('objs is not a list')
        return None
    for obj in objs:
        if not isinstance(obj, dict):
            logging.warning('obj is not a dict')
            return None
        for field in fields:
            if field not in obj:
                logging.warning('field missing from obj')
                return None
            if not isinstance(obj[field], basestring):
                logging.warning('field in obj not a string')
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
        hunt = Hunt.all().filter('name =', hunt_name).filter('owner =', self.user).get()
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
        answer_sets = []
        for clue in hunt.clues:
            if hunt.started:
                answers = [not team.has_clue_left(clue) for team in hunt.teams]
            else:
                answers = [False for team in hunt.teams]
            answer_sets.append({
                'question': clue.question,
                'answers': answers,
            })

        scores = []
        progresses = []
        for team in hunt.teams:
            scores.append(team.score())
            if team.remaining():
                progresses.append('%d left' % team.remaining())
            else:
                progresses.append(str(team.finish_time))

        logging.debug('ShowHunt answer_sets: %s' % answer_sets)
        self.response.out.write(utils.render('templates/hunt.html', {'hunt': hunt, 'answer_sets': answer_sets, 'scores': scores, 'progresses': progresses}))

    @utils.logged_in
    def post(self, hunt_id):
        hunt = get_hunt_by_id(hunt_id)
        if not hunt:
            self.redirect('/')
            return
        hunt.start()
        self.redirect('/hunt/%s' % hunt.key().id())


class Clues(webapp.RequestHandler):
    @utils.logged_in
    def get(self, hunt_id):
        hunt = get_hunt_by_id(hunt_id)
        if not hunt:
            self.redirect('/')
            return
        clues = list(Clue.all().filter('hunt =', hunt))
        self.response.out.write(utils.render('templates/clues.html', {
            'hunt': hunt,
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
                hunt.add_clue(clue_dict['question'], clue_dict['answer'])
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
            'hunt': hunt,
            'hunt_name': hunt.name,
            'started': bool(hunt.started),
            'teams': teams,
            'teams_json': json.dumps([{
                'id': team.key().id(),
                'name': team.name,
                'phone': team.phone,
                } for team in teams]),
            }))

    @utils.logged_in
    def post(self, hunt_id):
        hunt = get_hunt_by_id(hunt_id)
        if not hunt:
            self.redirect('/')
            return
        teams_list = parse_json_objs(self.request.get('teams-list'), ['name', 'phone'])
        if not teams_list:
            self.redirect('/')
            return
        if not all(PHONE_NUMBER_RE.match(team['phone']) for team in teams_list):
            self.redirect('/')
            return
        if hunt.started:
            # TODO update existing teams
            pass
        else:
            for team in Team.all().filter('hunt =', hunt):
                team.delete()

            for team_dict in teams_list:
                hunt.add_team(team_dict['name'], team_dict['phone'])
        self.redirect('/hunt/%s/teams' % hunt.key().id())
