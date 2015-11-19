"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

# from django.test import TestCase
from django.test import Client
# from models import Post
from django.contrib.auth.models import User
import unittest

# class Test(TestCase):
#     def setup(self):
#         Post.objects.create(title="test")

#     def test_basic_addition(self):
#         post = Post.objects.get(title="test")
#         self.assertEqual(post.id, 1)


class Auth(unittest.TestCase):

    def setUp(self):
        self.client = Client()

    def test_register(self):
        # Issue a GET request.
        response = self.client.post('http://127.0.0.1:8000/api/v6/auth/register/',
                                    {"token": "e622c330c77a17c8426e638d7a85da6c2ec9f455",
                                     "username": "unit_test",
                                     "password": "1",
                                     "email": "a.b@gmail.com"})

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        response = self.client.post('http://127.0.0.1:8000/api/v6/auth/login/',
                                    {"token": "e622c330c77a17c8426e638d7a85da6c2ec9f455",
                                     "username": "unit_test",
                                     "password": "1",
                                     "email": "a.b@gmail.com"})
        self.assertEqual(response.status_code, 200)

    def get_user(self, username):
        user = User.objects.get(username=username)
        return user

    def test_follow(self):
        response = self.client.get('http://127.0.0.1:8000/api/v6/auth/follow/',
                                   {"token": "123",
                                    "username": "unit_test",
                                    "password": "1",
                                    "email": "a.b@gmail.com"})
        self.assertEqual(response.status_code, 200)

    def test_unfollow(self):
        response = self.client.get('http://127.0.0.1:8000/api/v6/auth/unfollow/',
                                   {"token": "123",
                                    "username": "unit_test",
                                    "password": "1",
                                    "email": "a.b@gmail.com"})
        self.assertEqual(response.status_code, 200)

    def test_followers(self):
        response = self.client.get('http://127.0.0.1:8000/api/v6/auth/followers/',
                                   {"token": "123",
                                    "username": "unit_test",
                                    "password": "1",
                                    "email": "a.b@gmail.com"})
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
