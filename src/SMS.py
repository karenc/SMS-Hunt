from google.appengine.ext import webapp
from local_settings import account_settings
import os
from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch

class SendSMS(webapp.RequestHandler):
    
    def get(self):
        """Show form to send sms"""
        
        path = os.path.join(os.path.dirname(__file__), 'templates/send_sms.html')
        self.response.out.write(template.render(path, {}))        
        
    def post(self):
        """Take the params and send the form"""
        
        recipient = self.request.get('recipient')
        message = self.request.get('message')

        if recipient and message:
            
            url = 'https://www.esendex.com/secure/messenger/formpost/SendSMS.aspx'
            
            form_fields = {
                'EsendexUsername' : account_settings['username'],
                'EsendexPassword' : account_settings['password'],
                'EsendexAccount' : account_settings['account'],
                'EsendexRecipient' : recipient,
                'EsendexBody' : message,
                }
            form_data = urllib.urlencode(form_fields)
            
            result = urlfetch.fetch(url=url, 
                                    method=urlfetch.POST, 
                                    payload=form_data, 
                                    headers={'Content-Type': 'application/x-www-form-urlencoded'})
        
        path = os.path.join(os.path.dirname(__file__), 'templates/sent_sms.html')
        self.response.out.write(template.render(path, {}))   
        
    
        
class PollSMS(webapp.RequestHandler):
    """Go and fetch smss from inbox"""
    
    def get(self):
        """"""