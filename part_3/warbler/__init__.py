import os
from dotenv import load_dotenv

from warbler.root.views import root_views
from warbler.auth.views import auth_views
from warbler.users.views import users_views
from warbler.messages.views import messages_views
from warbler.likes.views import likes_views



from flask import (Flask, render_template, session, g)
from flask_debugtoolbar import DebugToolbarExtension

from warbler.forms import CSRFProtection

from warbler.database import connect_db
from warbler.users.models import User

load_dotenv()

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.register_blueprint(root_views)
app.register_blueprint(auth_views)
app.register_blueprint(users_views)
app.register_blueprint(likes_views)
app.register_blueprint(messages_views)


# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ['DATABASE_URL'].replace("postgres://", "postgresql://"))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
toolbar = DebugToolbarExtension(app)

connect_db(app)


##############################################################################
# Before/after request and error handler


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


@app.before_request
def add_csrf_only_form():
    """Add a CSRF-only form so that every route can use it."""

    g.csrf_form = CSRFProtection()


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Log out user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.errorhandler(404)
def page_not_found(e):
    """404 NOT FOUND page."""

    return render_template('404.html'), 404


@app.after_request
def add_header(response):
    """Add non-caching headers on every request."""

    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control
    response.cache_control.no_store = True
    return response








