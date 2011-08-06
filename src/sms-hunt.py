import logging

from google.appengine.dist import use_library
use_library('django', '1.2')
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from SMS import SendSMS, PollSMS
from controller import Index, CreateHunt, ShowHunt, Clues
import utils

Application = webapp.WSGIApplication(
    [('/', Index),
     ('/send_sms', SendSMS),
     ('/poll_sms', PollSMS),
     ('/create-hunt', CreateHunt),
     ('/hunt/(.*)/clues', Clues),
     ('/hunt/(.*)', ShowHunt),
     ],
    debug=True)

def main():
    """Kicks everything off"""
    logging.getLogger().setLevel(logging.DEBUG)
    run_wsgi_app(Application)

if __name__ == "__main__":
    main()
