from google.appengine.ext import webapp
from local_settings import account_settings
import os
from google.appengine.ext.webapp import template

class SendSMS(webapp.RequestHandler):
    
    def get(self):
        """Show form to send sms"""
        
        path = os.path.join(os.path.dirname(__file__), 'templates/send_sms.html')
        self.response.out.write(template.render(path, {}))        
        
    def post(self):
        """Take the params and send the form"""
        
        
    
        
class PollSMS(webapp.RequestHandler):
    """Go and fetch smss from inbox"""
    
    def get(self):
        """"""