"""Message model tests."""
from utils import *
from app import app
from models import db, User, Message, Follows
from unittest import TestCase
import os
from sqlalchemy import exc


# run these tests like:
#
#    python -m unittest test_user_model.py


# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database


# Now we can import app


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data
db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_message_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            image_url=None
        )
        db.session.add(u)

        m = Message(
            text="tester warble",
            user_id=f'{u.id}'
        )

        db.session.add(m)
        u.messages.append(m)

        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 1)
        self.assertEqual(u.messages[0].text, "tester warble")
