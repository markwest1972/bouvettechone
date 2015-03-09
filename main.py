import logging
import datetime
import os
import Cookie
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

COOKIE_NAME = '20140206-techone'

class User(db.Model):

    sessionIds = db.StringListProperty()
    date = db.DateTimeProperty(auto_now = True)

    def attends(self, sessionId = None):
        return sessionIds.index(sessionId)

    def __str__(self):
        return '%s %s %s' % (self.key(), self.sessionIds, self.date)

class Session:

    def __init__(self, id, title, tags = None, author = None, description = None):
        self.id = id
        self.title = title
        self.tags = tags
        self.author = author
        self.count = 0
        if len(description) == 0:
            description = 'Beskrivelse mangler'
        self.description = description

class UserBaseHandler(webapp.RequestHandler):

    def getUser(self, create = True):
        user = None
        try:
            cookie = Cookie.SimpleCookie(os.environ['HTTP_COOKIE'])
            userKey = cookie[COOKIE_NAME].value
            user = db.get(db.Key(userKey))
            if (user is None):
                logging.warning('returning user not found in datastore: ' + userKey)
                raise KeyError()
            logging.debug('returning user: ' + str(user.key()))
        except (Cookie.CookieError, KeyError):
            pass
        if (user is None and create):
            user = User()
            user.put()
            logging.info('new user: ' + str(user.key()))
            expires = datetime.datetime.now() + datetime.timedelta(days=100)
            cookie = Cookie.SimpleCookie()
            cookie[COOKIE_NAME] = user.key()
            cookie[COOKIE_NAME]['expires'] = expires.strftime("%a, %d-%b-%Y %H:%M:%S CET")
            self.response.headers['Set-Cookie'] = cookie.output()[12:]
        return user

class MainPage(UserBaseHandler):

    def get(self):
        template_values = {
            'sessions' : loadSessions(),
            'user' : self.getUser()
        }
        self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
        self.response.out.write(
            template.render(
                os.path.join(os.path.dirname(__file__), 'index.html'),
                template_values
            )
        )

def collect_stats():
    sessions = loadSessions()
    users = loadUsers()
    countT = 0
    countW = 0
    for session in sessions:
        session.count = 0
    for user in users:
        countT += 1
        if len(user.sessionIds) > 0:
            countW += 1
        for sessionId in user.sessionIds:
            matching = [session for session in sessions if session.id == sessionId]
            if len(matching) == 1:
                matching[0].count += 1

    sessions.sort(lambda x, y: y.count - x.count)

    return { 'sessions' : sessions, 'countT' : countT, 'countW' : countW,
             'countWO' : countT - countW }

def loadUsers():
    users =  memcache.get('users')
    if not users is None:
        return users
    users = User.all()
    if not memcache.add('users', users, 60 * 5):
        logging.error("Memcache add failed for users")
    return users

class StatsPage(webapp.RequestHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
        self.response.out.write(
            template.render(
                os.path.join(os.path.dirname(__file__), 'stats.html'),
                collect_stats()
            )
        )

class StatsDump(webapp.RequestHandler):

    def get(self):
        sessions = collect_stats()['sessions']
        self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'

        out = self.response.out
        for session in sessions:
            out.write("|".join(map(str, [session.id, session.title,
                                         session.author, session.count,
                                         session.description])) + "\n")

class FlushCache(webapp.RequestHandler):

    def get(self):
        self.response.out.write('Nice try, but flushing is disabled.') 
        """ Commented out: this code cannot be left runnable without implementing some kind of permission checking mechanism first."""
        """self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        self.response.out.write('Flushed cache: ' + str(memcache.flush_all()))
        q = db.GqlQuery("SELECT * FROM User")
        for user in q:
            user.delete()"""


class FlushSessions(webapp.RequestHandler):

    def get(self):
        codes = ['NETWORK FAILURE', 'ITEM MISSING', 'SUCCESSFUL']
        result = codes[memcache.delete('sessions')]
        self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        self.response.out.write('Flushed session cache: %s\n' % result)

class AttendHandler(UserBaseHandler):

    def get(self):
        self.post()

    def post(self):
        user = self.getUser(False)
        if not user is None:
            user.sessionIds = self.request.get('session', allow_multiple = True, default_value = [])
            user.put()
        else:
            logging.warning('post attempted for a non existing user')

        if self.request.get('redirect', default_value = None) is None:
            self.redirect('/')

def loadSessions():
    sessions =  memcache.get('sessions')
    if not sessions is None:
        return sessions
    sessions = []
    try:
        file = open(os.path.join(os.path.dirname(__file__), 'talks.txt'))
        try:
            n = 0
            for line in file:
                parts = line.split('|')
                n += 1
                sessions.append(Session('s_' + str(n), parts[1].strip(), parts[2].strip(), parts[3].strip(), parts[4].strip()))
        finally:
            file.close
    except IOError:
        pass
    if not memcache.add('sessions', sessions):
        logging.error('Memcache add failed for sessions')
    return sessions

application = webapp.WSGIApplication([
        ('/', MainPage),
        ('/attend', AttendHandler),
        ('/stats', StatsPage),
        ('/stats-dump', StatsDump),
        ('/flush', FlushCache),
        ('/flush-sessions', FlushSessions),
    ], debug=True)

def main():
    logging.getLogger().setLevel(logging.DEBUG)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
