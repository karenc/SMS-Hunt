from google.appengine.ext import webapp
from local_settings import account_settings
import os, urllib
from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch
import base64

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
            
            url = 'http://api.esendex.com/v1.0/messagedispatcher'
            encoded_username = base64.urlsafe_b64encode(account_settings['username']+':'+account_settings['password'])
            
            xml = """<?xml version='1.0' encoding='UTF-8'?><messages><accountreference>%s</accountreference><message><to>%s</to><body>%s</body></message></messages>""" % (account_settings['account'], recipient, message)  
            result = urlfetch.fetch(url=url, method=urlfetch.POST, payload=xml, headers={'Content-Type' : 'text/xml', 'Authorization' : "Basic %s" % (encoded_username[:-1])})
        
        path = os.path.join(os.path.dirname(__file__), 'templates/sent_sms.html')
        self.response.out.write(template.render(path, {}))   
        
    
        
class PollSMS(webapp.RequestHandler):
    """Go and fetch smss from inbox"""
    
    def get(self):
        """"""