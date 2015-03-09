import logging
import datetime
import os
import Cookie
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

class OutOfServicePage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
        self.response.out.write(
            template.render(
                os.path.join(os.path.dirname(__file__), 'outofservice.html'),
                { }
            )
        )

application = webapp.WSGIApplication([
        ('/.*', OutOfServicePage),\
    ], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
