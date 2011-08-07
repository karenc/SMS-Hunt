from google.appengine.ext import webapp
from local_settings import account_settings
import os, urllib
from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch
import base64
from xml.etree import ElementTree
import logging
from Hunt import *

def send(recipient, message):
    """Send this message to the specified recipient. Returns an HTTP
    code. If sending is false in account_settings, simply logs and
    returns 200."""
    logging.debug("Sending SMS to %s: %s" % (recipient, message))
    if not account_settings['sending']:
        return 200
    url = 'http://api.esendex.com/v1.0/messagedispatcher'
    encoded_username = base64.urlsafe_b64encode(account_settings['username']+':'+account_settings['password'])
            
    xml = """<?xml version='1.0' encoding='UTF-8'?><messages><accountreference>%s</accountreference><message><to>%s</to><body>%s</body></message></messages>""" % (account_settings['account'], recipient, message)  
    result = urlfetch.fetch(url=url, method=urlfetch.POST, payload=xml, headers={'Content-Type' : 'text/xml', 'Authorization' : "Basic %s" % (encoded_username)})
    return result.status_code

class AnswerHandler(webapp.RequestHandler):

    def post(self):
        body = self.request.body
        m = re.search('<MessageText>(.*?)</MessageText>')
        msg = m.group(1)
        m = re.search('<From>44(\d+)</From>')
        number_without_zero = m.group(1)

        if msg and number_without_zero:
            Team.deliver("0%s" % number_without_zero, msg)
            self.response.out.write("Delivered to app!")
        else:
            self.response.set_status(500)
            self.response.out.write("WTF Esendex?")

class SendSMS(webapp.RequestHandler):
    
    def get(self):
        """Show form to send sms"""
        
        path = os.path.join(os.path.dirname(__file__), 'templates/send_sms.html')
        self.response.out.write(template.render(path, {}))        
        
    def post(self):
        """Take the params and send the form"""
        
        recipient = self.request.get('recipient')
        message = self.request.get('message')
        template_values = {}
        if recipient and message:
            result = send(recipient, message)
            if result == 200:
                template_values['message'] = "Success!"
                
            
        path = os.path.join(os.path.dirname(__file__), 'templates/sent_sms.html')
        self.response.out.write(template.render(path, template_values))   
        
    
        
class PollSMS(webapp.RequestHandler):
    """Go and fetch smss from inbox"""
    
    def get(self):
        """fetch from inbox"""
        
        url = "http://api.esendex.com/v1.0/Inbox/Messages"
        encoded_username = base64.urlsafe_b64encode(account_settings['username']+':'+account_settings['password'])
        
        result = urlfetch.fetch(url=url, method=urlfetch.GET, headers={'Authorization' : "Basic %s" % (encoded_username)})

        root = ElementTree.fromstring(result.content)
        root.findall('{http://api.esendex.com/ns/}messageheader')
