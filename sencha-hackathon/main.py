from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from django.utils import simplejson as json
import logging
import datetime
import os

class ContactInfo(db.Model):
  eventid = db.StringProperty(required=False)
  username = db.StringProperty(required=True)
  twitterid = db.StringProperty(required=False)
  email = db.StringProperty(required=True)
  created = db.DateTimeProperty(auto_now_add=True)
  updated = db.DateTimeProperty(auto_now=True)
  
  def json(self):
    return {
      'eventid': self.eventid,
      'username': self.username,
      'twitterid': self.twitterid,
      'email': self.email,
    }
  

class MainHandler(webapp.RequestHandler):
  def get(self):
    data = {
      'contacts': ContactInfo.gql('ORDER BY updated DESC').fetch(1000)
    }
    path = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')
    self.response.out.write(template.render(path, data))
    
class JsonHandler(webapp.RequestHandler):
  def _encode(self, obj):
    if hasattr(obj, "json") and callable(getattr(obj, "json")):
      return obj.json()
    raise TypeError(errors.JSON_PARSE_ERROR % repr(obj))

  def get(self):
    contacts = ContactInfo.gql('ORDER BY updated DESC').fetch(1000)
    encoder = json.JSONEncoder()
    encoder.default = self._encode   # Monkey patching is fun :)
    message = encoder.encode(contacts)    
    self.response.out.write(message)
    
class FormHandler(webapp.RequestHandler):
  def get(self):
    path = os.path.join(os.path.dirname(__file__), 'templates', 'form.html')
    data = {}
    self.response.out.write(template.render(path, data))
    
  def post(self):
    kwargs = {
      'eventid': self.request.get('eventid'),
      'username': self.request.get('username'),
      'twitterid': self.request.get('twitterid'),
      'email': self.request.get('email')
    }
    try:
      info = ContactInfo(**kwargs)
      key = db.put(info)
      self.redirect('/')
    except db.BadValueError, e:
      message = "Could not create a new contact (Missing fields?)"
      logging.exception(message)
      kwargs['error'] = message
      path = os.path.join(os.path.dirname(__file__), 'templates', 'form.html')
      self.response.set_status(400, message)
      self.response.out.write(template.render(path, kwargs))
    
def main():
  application = webapp.WSGIApplication([
    ('/', MainHandler),
    ('/form', FormHandler),
    ('/json', JsonHandler),
  ], debug=True)
  util.run_wsgi_app(application)

if __name__ == '__main__':
  main()
