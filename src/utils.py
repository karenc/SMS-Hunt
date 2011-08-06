import os

from google.appengine.ext.webapp import template
from google.appengine.api import users

def logged_in(func):
    def _inner(self, *args, **kwargs):
        self.user = users.get_current_user()
        if not self.user:
            self.redirect(users.create_login_url(self.request.uri))
            return
        return func(self, *args, **kwargs)
    return _inner

def render(relative_path, *args, **kwargs):
    path = os.path.join(os.path.dirname(__file__), relative_path)
    return template.render(path, *args, **kwargs)
