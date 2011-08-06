from google.appengine.dist import use_library
use_library('django', '1.2')
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from SMS import SendSMS, PollSMS
from hunt import CreateHunt, ShowHunt
import utils

class Index(webapp.RequestHandler):
    
    @utils.logged_in
    def get(self):
        self.response.out.write(utils.render('templates/index.html', {}))

        
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
