from google.appengine.api import users

def logged_in(func):
    def _inner(self, *args, **kwargs):
        self.user = users.get_current_user()
        if not self.user:
            self.redirect(users.create_login_url(self.request.uri))
            return
        return func(self, *args, **kwargs)
    return _inner
