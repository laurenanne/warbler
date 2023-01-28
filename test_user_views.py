
from utils import *
from unittest import TestCase
from app import app, CURR_USER_KEY
from models import db, Follows, Likes, User, Message
from sqlalchemy import exc
from flask import session


app.config['TESTING'] = True

db.drop_all()
db.create_all()


class UserViewsTestCase(TestCase):
    """Tests for views of API"""

    def setUp(self):

        User.query.delete()

        user = User.signup(username="user1", email="user@test.com",password="password", image_url=None)
        
        user2 = User.signup(username="user2", email="user2@test.com",password="password2", image_url=None)
        
        user3 = User.signup(username="user3", email="user3@test.com",password="password3", image_url=None)

        db.session.commit()

        self.user_id = user.id
        self.user2_id = user2.id
        self.user3_id = user3.id

        fol = Follows(user_being_followed_id = self.user2_id, user_following_id = self.user_id)
        db.session.add(fol)
        db.session.commit()

        message = Message(id = 1000, text="This is a warble", user_id = self.user_id)
        message2 = Message(id = 1001, text="This is a warble I liked", user_id = self.user2_id)
        
        db.session.add(message)
        db.session.add(message2)
        db.session.commit() 


    def tearDown(self):
        """Clean up fouled transactions"""

        db.session.rollback()


    
    def test_home(self):
        with app.test_client() as client:
            resp = client.get('/')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('New to Warbler',html)



    def test_signup(self):
        with app.test_client() as client:
            resp = client.get('/signup')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Join Warbler today.',html)


    def test_login(self):
        with app.test_client() as client:
            resp = client.get('/login')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Welcome back.',html)

    def test_logout(self):
        with app.test_client() as client:
            resp = client.get('/logout')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, "/login")
            self.assertIn(('message', 'You have successfully logged out'),session['_flashes'])



    def test_user_lists(self):
        with app.test_client() as client:
            resp = client.get('/users')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('@user1',html)


    def test_show_user(self):
        message = Message(text="This is a warble", user_id = self.user_id)

        db.session.add(message)
        db.session.commit()

        with app.test_client() as client:
            resp = client.get(f'/users/{self.user_id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('@user1',html)
            self.assertIn('This is a warble',html)

    def test_show_users_following(self):
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id
                
            resp = client.get(f'/users/{self.user_id}/following')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("@user2", html)

           
    def test_show_users_followers(self):
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user2_id
                
            resp = client.get(f'/users/{self.user2_id}/followers')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("@user1", html)


    def test_add_follow(self):
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id
                
            resp = client.post(f'/users/follow/{self.user3_id}')
    
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/users/{self.user_id}/following')


    def test_remove_follow(self):
        user = User.query.get(self.user_id)
        
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id
                
            resp = client.post(f'/users/stop-following/{self.user2_id}')
    
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/users/{self.user_id}/following')

            self.assertEqual(len(user.following), 0)
       

    def test_user_delete(self):
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user3_id
                
            resp = client.post('/users/delete')
    
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, '/signup')
            user = User.query.get(self.user3_id)
            self.assertIs(user, None)   


    def test_user_add_like(self):
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id
                
            resp = client.post(f'/users/add_like/1001')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/users/{self.user_id}/likes')

        
    def test_view_like(self):
  
        l = Likes(user_id = self.user_id, message_id = 1001)
        db.session.add(l)
        db.session.commit()

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id
                
            resp = client.get(f'/users/{self.user_id}/likes')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("This is a warble I liked", html)
        
            
    def test_unauthorized_view_like(self):
  
        l = Likes(user_id = self.user_id, message_id = 1001)
        db.session.add(l)
        db.session.commit()

        with app.test_client() as client:
            resp = client.get(f'/users/{self.user_id}/likes')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 302)
            self.assertIn(('danger', 'Access unauthorized.'),session['_flashes'])

    
    def test_unauthorized_show_users_following(self):
        with app.test_client() as client:
    
            resp = client.get(f'/users/{self.user_id}/following')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 302)
            self.assertIn(('danger', 'Access unauthorized.'),session['_flashes'])


           
    def test_unauthorized_show_users_followers(self):
        with app.test_client() as client:
          
            resp = client.get(f'/users/{self.user2_id}/followers')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 302)
            self.assertIn(('danger', 'Access unauthorized.'),session['_flashes'])

