
from google.appengine.dist import use_library
use_library('django', '1.2')
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from SMS import SendSMS, PollSMS, AnswerHandler
from controller import Index, CreateHunt, ShowHunt, Clues, Teams
import utils
import logging

Application = webapp.WSGIApplication(
    [('/', Index),
     ('/send_sms', SendSMS),
     ('/poll_sms', PollSMS),
     ('/create-hunt', CreateHunt),
     ('/hunt/(.*)/clues', Clues),
     ('/hunt/(.*)/teams', Teams),
     ('/hunt/(.*)', ShowHunt),
     ('/answer-handler', AnswerHandler),
     ],
    debug=True)

def main():
    """Kicks everything off"""
    logging.getLogger().setLevel(logging.DEBUG)
    run_wsgi_app(Application)

if __name__ == "__main__":
    main()
