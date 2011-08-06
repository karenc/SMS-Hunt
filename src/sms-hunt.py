from google.appengine.dist import use_library
use_library('django', '1.2')
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch
from google.appengine.ext import db
import os
from SMS import SendSMS, PollSMS

def logged_in(func):
    def _inner(self, *args, **kwargs):
        self.user = users.get_current_user()
        if not self.user:
            self.redirect(users.create_login_url(self.request.uri))
            return
        return func(self, *args, **kwargs)
    return _inner

class Index(webapp.RequestHandler):
    
    def get(self):
        user = users.get_current_user()

        if user:
            pass
        else:
            self.redirect(users.create_login_url(self.request.uri))
            
        
        path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        self.response.out.write(template.render(path, {}))

        
Application = webapp.WSGIApplication(
    [('/', Index),
     ('/send_sms', SendSMS),
     ('/poll_sms', PollSMS),
     ],
    debug=True)

def main():
    """Kicks everything off"""
    run_wsgi_app(Application)

if __name__ == "__main__":
    main()
