# -*- coding: utf-8 -*-
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

# from django.test import TestCase
from django.test import Client
from models import Category, Post, Comments
from django.contrib.auth.models import User
import unittest
from tastypie.models import ApiKey


# class Test(TestCase):
#     def setup(self):
#         Post.objects.create(title="test")

#     def test_basic_addition(self):
#         post = Post.objects.get(title="test")
#         self.assertEqual(post.id, 1)


class AuthTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        User.objects.create(username='amir', email='a.ab@yahoo.com', password='1')
        User.objects.create(username='vahid', email='a.abc@yahoo.com', password='1')
        User.objects.create(username='saeed', email='a.abd@yahoo.com', password='1')
        User.objects.create(username='unit_test', email='a.abds@yahoo.com', password='1')
        # self.create_category()

    def tearDown(self):
        User.objects.all().delete()
        ApiKey.objects.all().delete()

    def test_register(self):
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
        user1 = User.objects.get(username='unit_test')
        user2 = User.objects.get(username='amir')
        api_key, created = ApiKey.objects.get_or_create(user=user1)

        response = self.client.get('http://127.0.0.1:8000/api/v6/auth/follow/',
                                   {"token": api_key.key,
                                    "user_id": user2.id})
        self.assertEqual(response.status_code, 200)

    def test_unfollow(self):
        user1 = User.objects.get(username='unit_test')
        user2 = User.objects.get(username='amir')
        api_key, created = ApiKey.objects.get_or_create(user=user1)

        response = self.client.get('http://127.0.0.1:8000/api/v6/auth/unfollow/',
                                   {"token": api_key.key,
                                    "user_id": user2.id})
        self.assertEqual(response.status_code, 200)

    def test_followers(self):
        user1 = User.objects.get(username='unit_test')
        user2 = User.objects.get(username='amir')
        api_key, created = ApiKey.objects.get_or_create(user=user2)

        url = 'http://127.0.0.1:8000/api/v6/auth/followers/%s/' % str(user1.id)

        response = self.client.get(url, {'token': api_key.key})
        self.assertEqual(response.status_code, 200)

    def test_following(self):
        user1 = User.objects.get(username='unit_test')
        user2 = User.objects.get(username='amir')
        api_key, created = ApiKey.objects.get_or_create(user=user2)

        url = 'http://127.0.0.1:8000/api/v6/auth/followers/%s/' % str(user1.id)

        response = self.client.get(url, {'token': api_key.key})
        self.assertEqual(response.status_code, 200)

    def test_profile(self):
        user = User.objects.get(username='amir')
        api_key, created = ApiKey.objects.get_or_create(user=user)

        response = self.client.get('http://127.0.0.1:8000/api/v6/auth/user/%s/' % str(user.id),
                                   {"token": api_key.key})
        self.assertEqual(response.status_code, 200)

    def test_update_profile(self):
        user = User.objects.get(username='amir')
        api_key, created = ApiKey.objects.get_or_create(user=user)
        url = 'http://127.0.0.1:8000/api/v6/auth/user/update/?token=%s' % str(api_key.key)
        response = self.client.post(url, {'name': 'amir_ali',
                                          'jens': 'M',
                                          'bio': 'salam'})
        self.assertEqual(response.status_code, 200)

    def test_search_user(self):
        user = User.objects.get(username='amir')
        api_key, created = ApiKey.objects.get_or_create(user=user)

        response = self.client.get('http://127.0.0.1:8000/api/v6/auth/user/search/',
                                   {"token": api_key.key,
                                    "q": 'vahid'})
        self.assertEqual(response.status_code, 200)


class CategoryTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        User.objects.create(username='amir', email='a.ab@yahoo.com', password='1')
        Category.objects.create(title='sport', image='/home/amir/Pictures/images.jpg')
        # self.create_category()

    def tearDown(self):
        User.objects.all().delete()
        ApiKey.objects.all().delete()
        Category.objects.all().delete()

    def test_show_category(self):
        user = User.objects.get(username='amir')
        api_key, created = ApiKey.objects.get_or_create(user=user)
        cat = Category.objects.get(title='sport')
        response = self.client.get('http://127.0.0.1:8000/api/v6/category/%s/?token=%s' % (str(cat.id), str(api_key.key)))
        self.assertEqual(response.status_code, 200)

    def test_all_category(self):
        user = User.objects.get(username='amir')
        api_key, created = ApiKey.objects.get_or_create(user=user)
        response = self.client.get('http://127.0.0.1:8000/api/v6/category/all/?token=%s' % str(api_key.key))
        self.assertEqual(response.status_code, 200)


class CommentTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username='amir', email='a.ab@yahoo.com', password='1')
        self.cat = Category.objects.create(title='sport', image='/home/amir/Pictures/images.jpg')
        self.post = Post.objects.create(image='/home/amir/Pictures/images.jpg', category=self.cat, user=self.user)
        self.comment = Comments.objects.create(comment='very nicee', post=self.post, user=self.user)

    def tearDown(self):
        User.objects.all().delete()
        Post.objects.all().delete()
        Category.objects.all().delete()
        Comments.objects.all().delete()
        ApiKey.objects.all().delete()

    def test_post_comments(self):
        url = 'http://127.0.0.1:8000/api/v6/comment/showComments/post/%s/' % str(self.post.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_add_comment(self):
        api_key, created = ApiKey.objects.get_or_create(user=self.user)
        url = 'http://127.0.0.1:8000/api/v6/comment/add/post/%s/?token=%s' % (str(self.post.id), str(api_key.key))
        response = self.client.post(url, {'comment': 'niceeee post'})
        self.assertEqual(response.status_code, 200)

    def test_delete_comment(self):
        api_key, created = ApiKey.objects.get_or_create(user=self.user)
        url = "http://127.0.0.1:8000/api/v6/comment/delete/%s/?token=%s" % (str(self.comment.id), str(api_key.key))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()


# def create_category(self):
#         name_list = ['ورزشی', 'سیاسی', 'علمی', 'سرگرمی']
#         for name in name_list:
#             try:
#                 Category.objects.create(title=name)
#             except Exception as e:
#                 print str(e)


# def get_category(self):
#     category = Category.objects.order_by('-id')[:1]
#     return category
