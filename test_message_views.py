"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py

from utils import *
from unittest import TestCase
from app import app, CURR_USER_KEY
from models import db, connect_db, Message, User
from flask import session


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

app.config['TESTING'] = True

db.drop_all()
db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/users/{self.testuser.id}')
            
            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_unauthorized_add_message(self):
        """Are we prohibited from adding a message when not logged in?"""

        with self.client as c:
            resp = c.post("/messages/new", data={"text": "Hi Ya"})

            # Make sure it redirects and message flashes
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, '/')
            self.assertIn(('danger', 'Access unauthorized.'),session['_flashes'])
        

    def test_delete_message(self):
        """Can you delete a message?"""

        message = Message(id = 1000, text="This is a warble", user_id = self.testuser.id)
        db.session.add(message)
        db.session.commit() 

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post("/messages/1000/delete")

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/users/{self.testuser.id}')
            
            msg = Message.query.get(1000)
            self.assertEqual(msg, None)


    def test_unauthorized_delete_message(self):
        """Can you delete a message if not logged in or not the user?"""

        message = Message(id = 1000, text="This is a warble", user_id = self.testuser.id)
        db.session.add(message)
        db.session.commit() 

        with self.client as c:
            
            resp = c.post("/messages/1000/delete")

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location,'/')
            self.assertIn(('danger', 'Access unauthorized.'),session['_flashes'])
        
            