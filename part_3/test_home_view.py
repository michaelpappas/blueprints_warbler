"""User View tests."""

# run these tests like:
#
#    FLASK_DEBUG=False python -m unittest test_message_views.py


import os
from unittest import TestCase

from bs4 import BeautifulSoup

from models import Follows, Like, Message, User, db, connect_db

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app, CURR_USER_KEY

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

connect_db(app)

db.drop_all()
db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False

class HomeViewTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)

        db.session.add_all([u1])
        db.session.commit()

        self.u1_id = u1.id

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_home_logged_in(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id
            resp = c.get(
                "/",
                follow_redirects=True,)
                
            self.assertEqual(resp.status_code, 200)
            self.assertIn("@u1", str(resp.data))
            self.assertIn("Log out", str(resp.data))

    def test_home_logged_out(self):
        with self.client as c:

            resp = c.get(
                "/",
                follow_redirects=True,)
                
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Sign up", str(resp.data))
            self.assertIn("Log in", str(resp.data))
            self.assertIn("Happening?", str(resp.data))


