# -*- coding: utf-8 -*-
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

# from django.test import TestCase
from django.test import Client
from models import Category
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
        self.create_users()
        # self.create_category()

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
                                     "password": "1"})
        self.assertEqual(response.status_code, 200)

    def test_follow(self):
        user1 = self.get_user_by_username("unit_test")
        user2 = self.get_user_by_username("amir")

        response = self.client.get('http://127.0.0.1:8000/api/v6/auth/follow/',
                                   {"token": user1.api_key.key,
                                    "user_id": user2.id})
        self.assertEqual(response.status_code, 200)

    def test_unfollow(self):
        user1 = self.get_user_by_username("unit_test")
        user2 = self.get_user_by_username("amir")

        response = self.client.get('http://127.0.0.1:8000/api/v6/auth/unfollow/',
                                   {"token": user1.api_key.key,
                                    "user_id": user2.id})
        self.assertEqual(response.status_code, 200)

    def test_followers(self):
        user1 = self.get_user_by_username("amir")
        user2 = self.get_user_by_username("unit_test")
        url = 'http://127.0.0.1:8000/api/v6/auth/followers/%s' % str(user1.id)

        response = self.client.get(url, {'token': user2.api_key.key})
        self.assertEqual(response.status_code, 200)

    def test_following(self):
        user1 = self.get_user_by_username("amir")
        user2 = self.get_user_by_username("unit_test")
        url = 'http://127.0.0.1:8000/api/v6/auth/followers/%s' % str(user1.id)

        response = self.client.get(url, {'token': user2.api_key.key})
        self.assertEqual(response.status_code, 200)

    def test_profile(self):
        user = self.get_user_by_username("amir")

        response = self.client.get('http://127.0.0.1:8000/api/v6/auth/user/%s' % str(user.id),
                                   {"token": user.api_key.key})
        self.assertEqual(response.status_code, 200)

    def test_update_profile(self):
        user = self.get_user_by_username("amir")

        response = self.client.get('http://127.0.0.1:8000/api/v6/auth/user/update/',
                                   {"token": user.api_key.key})
        self.assertEqual(response.status_code, 200)

    def test_search_user(self):
        user = self.get_user_by_username("amir")

        response = self.client.get('http://127.0.0.1:8000/api/v6/auth/user/search/',
                                   {"token": user.api_key.key,
                                    "q": 'vahid'})
        self.assertEqual(response.status_code, 200)

    # Tools
    def get_user_by_username(self, username):
        user = User.objects.get(username=username)
        return user

    def get_users(self):
        users = User.objects.order_by('-id')[:3]
        return users

    def create_users(self):
        username = ['amir1', 'vahid1', 'saeed1']
        email = ['a.ab@yahoo.com', 'a.abc@yahoo.com', 'a.abd@gmail.com']
        for index, value in enumerate(username):
            try:
                User.objects.create(username=value, email=email[index], password='1')
            except Exception as e:
                print str(e)

    def create_category(self):
        name_list = ['ورزشی', 'سیاسی', 'علمی', 'سرگرمی']
        for name in name_list:
            try:
                Category.objects.create(title=name)
            except Exception as e:
                print str(e)

    def get_category(self):
        category = Category.objects.order_by('-id')[:1]
        return category


if __name__ == '__main__':
    unittest.main()
