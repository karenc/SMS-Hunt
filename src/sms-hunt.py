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
from hunt import CreateHunt, ShowHunt
import utils

class Index(webapp.RequestHandler):
    
    @utils.logged_in
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        self.response.out.write(template.render(path, {}))

        
Application = webapp.WSGIApplication(
    [('/', Index),
     ('/send_sms', SendSMS),
     ('/poll_sms', PollSMS),
     ('/create-hunt', CreateHunt),
     ('/hunt/(.*)', ShowHunt),
     ],
    debug=True)

def main():
    """Kicks everything off"""
    run_wsgi_app(Application)

if __name__ == "__main__":
    main()
