"""User model tests."""
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

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_repr(self):
        """Does repr method work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.commit()

        self.assertEqual(
            u.__repr__(), f'<User #{u.id}: testuser, test@test.com>')

    def test_is_following(self):
        """Does is following method work?"""

        user1 = User(
            email="user1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )

        user2 = User(
            email="user2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
        )

        db.session.add(user1)
        db.session.add(user2)

        """adds follow and checks that user1 following user2"""
        user1.following.append(user2)

        db.session.commit()

        self.assertEqual(
            user1.is_following(user2), 1)

        """removes follow and checks that user1 not following user2"""
        user1.following.remove(user2)
        db.session.commit()

        self.assertEqual(
            user1.is_following(user2), False)

    def test_is_followed(self):
        """Does is followed method work?"""

        user1 = User(
            email="user1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )

        user2 = User(
            email="user2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
        )

        db.session.add(user1)
        db.session.add(user2)

        """adds follow and checks that user1 is followed by user2"""
        user2.following.append(user1)
        db.session.commit()

        self.assertEqual(
            user1.is_followed_by(user2), 1)

        """removes follow and checks that user1 is followed by user2"""
        user2.following.remove(user1)
        db.session.commit()

        self.assertEqual(
            user1.is_followed_by(user2), False)

    def test_signup(self):
        """Is user successfully created?"""

        sign_in = User.signup(
            email="testuser1", username="user1@test.com", password="HASHED_PASSWORD", image_url=None)

        db.session.add(sign_in)
        db.session.commit()

        self.assertTrue(sign_in)

    def test_signup_missing_email(self):
        """Is error raised when invalid email"""

        sign_in = User.signup(
            email=None, username="user1@test.com", password="HASHED_PASSWORD", image_url=None)

        db.session.add(sign_in)

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_signup_missing_username(self):
        """Is error raised when invalid username"""

        sign_in = User.signup(
            email='user1@test.com',
            username=None,
            password="HASHED_PASSWORD", image_url=None
        )
        db.session.add(sign_in)

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_signup_missing_password(self):
        """Is error raised when password is None"""

        with self.assertRaises(ValueError) as context:

            User.signup(
                email='user1@test.com',
                username="testuser1",
                password=None, image_url=None)

    def test_signup_empty_password(self):
        """Is error raised when password is empty"""

        with self.assertRaises(ValueError) as context:

            User.signup(
                email='user1@test.com',
                username="testuser1",
                password="", image_url=None)

    def test_authenticate(self):
        """Is user successfully authenticated?"""

        user = User.signup(
            email='user1@test.com',
            username="testuser1",
            password="password", image_url=None)
        db.session.add(user)

        auth = User.authenticate(
            username="testuser1", password="password")

        db.session.add(auth)
        db.session.commit()

        self.assertEqual(user.id, auth.id)

    def test_auth_invalid_username(self):
        """Is user successfully authenticated?"""

        user = User.signup(
            email='user1@test.com',
            username="testuser1",
            password="password", image_url=None)
        db.session.add(user)

        auth = User.authenticate(
            username="testuser2", password="password")

        self.assertFalse(auth)

    def test_auth_invalid_password(self):
        """Is user successfully authenticated?"""

        user = User.signup(
            email='user1@test.com',
            username="testuser1",
            password="password", image_url=None)
        db.session.add(user)

        auth = User.authenticate(
            username="testuser1", password="passwd23")

        self.assertFalse(auth)
