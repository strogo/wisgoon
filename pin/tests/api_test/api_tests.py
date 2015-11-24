# -*- coding: utf-8 -*-
from django.test import Client
from pin.models import Category, Post, Comments
from django.contrib.auth.models import User
import unittest
from tastypie.models import ApiKey
import os
from django.conf import settings
from user_profile.models import Profile


class AuthTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.amir, created = User.objects.get_or_create(username='amir', email='a.ab@yahoo.com', password='1')
        self.vahid, created = User.objects.get_or_create(username='vahid', email='a.abc@yahoo.com', password='1')

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
        api_key, created = ApiKey.objects.get_or_create(user=self.amir)
        response = self.client.get('http://127.0.0.1:8000/api/v6/auth/follow/',
                                   {"token": api_key.key,
                                    "user_id": self.vahid.id})
        self.assertEqual(response.status_code, 200)

    def test_unfollow(self):
        api_key, created = ApiKey.objects.get_or_create(user=self.amir)
        response = self.client.get('http://127.0.0.1:8000/api/v6/auth/unfollow/',
                                   {"token": api_key.key,
                                    "user_id": self.vahid.id})
        self.assertEqual(response.status_code, 200)

    def test_followers(self):
        api_key, created = ApiKey.objects.get_or_create(user=self.amir)
        url = 'http://127.0.0.1:8000/api/v6/auth/followers/%s/' % str(self.vahid.id)

        response = self.client.get(url, {'token': api_key.key})
        self.assertEqual(response.status_code, 200)

    def test_following(self):
        api_key, created = ApiKey.objects.get_or_create(user=self.amir)
        url = 'http://127.0.0.1:8000/api/v6/auth/followers/%s/' % str(self.vahid.id)

        response = self.client.get(url, {'token': api_key.key})
        self.assertEqual(response.status_code, 200)

    def test_profile(self):
        api_key, created = ApiKey.objects.get_or_create(user=self.amir)
        response = self.client.get('http://127.0.0.1:8000/api/v6/auth/user/%s/' % str(self.amir.id),
                                   {"token": api_key.key})
        self.assertEqual(response.status_code, 200)

    def test_update_profile(self):
        api_key, created = ApiKey.objects.get_or_create(user=self.amir)
        url = 'http://127.0.0.1:8000/api/v6/auth/user/update/?token=%s' % str(api_key.key)
        response = self.client.post(url, {'name': 'amir_ali',
                                          'jens': 'M',
                                          'bio': 'salam'})
        self.assertEqual(response.status_code, 200)

    def test_search_user(self):
        api_key, created = ApiKey.objects.get_or_create(user=self.amir)
        response = self.client.get('http://127.0.0.1:8000/api/v6/auth/user/search/',
                                   {"token": api_key.key,
                                    "q": 'vahid'})
        self.assertEqual(response.status_code, 200)


class CategoryTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username='amir', email='a.ab@yahoo.com', password='1')
        self.cat = Category.objects.create(title='sport', image='/home/amir/Pictures/images.jpg')
        # self.create_category()

    def tearDown(self):
        User.objects.all().delete()
        ApiKey.objects.all().delete()
        Category.objects.all().delete()

    def test_show_category(self):
        api_key, created = ApiKey.objects.get_or_create(user=self.user)
        response = self.client.get('http://127.0.0.1:8000/api/v6/category/%s/?token=%s' % (str(self.cat.id), str(api_key.key)))
        self.assertEqual(response.status_code, 200)

    def test_all_category(self):
        api_key, created = ApiKey.objects.get_or_create(user=self.user)
        response = self.client.get('http://127.0.0.1:8000/api/v6/category/all/?token=%s' % str(api_key.key))
        self.assertEqual(response.status_code, 200)


class CommentTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username='amir', email='a.ab@yahoo.com', password='1')
        self.cat = Category.objects.create(title='sport',
                                           image='pin/blackhole/images/o/unittest_image.jpg')
        self.post = Post.objects.create(image="pin/blackhole/images/o/unittest_image.jpg",
                                        category=self.cat,
                                        user=self.user)
        self.comment = Comments.objects.create(comment='very nicee',
                                               object_pk=self.post,
                                               user=self.user)

    def tearDown(self):
        User.objects.all().delete()
        ApiKey.objects.all().delete()
        Category.objects.all().delete()
        Post.objects.all().delete()
        Comments.objects.all().delete()

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


class LikeTestcase(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username='amir', email='a.ab@yahoo.com', password='1')
        self.cat = Category.objects.create(title='sport',
                                           image='pin/blackhole/images/o/unittest_image.jpg')
        self.post = Post.objects.create(image="pin/blackhole/images/o/unittest_image.jpg",
                                        category=self.cat,
                                        user=self.user)

    def tearDown(self):
        User.objects.all().delete()
        ApiKey.objects.all().delete()
        Category.objects.all().delete()
        Post.objects.all().delete()

    def test_like_post(self):
        api_key, created = ApiKey.objects.get_or_create(user=self.user)
        url = "http://127.0.0.1:8000/api/v6/like/post/%s/?token=%s" % (str(self.post.id), str(api_key.key))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_post_likers(self):
        url = "http://127.0.0.1:8000/api/v6/like/likers/post/%s/" % str(self.post.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class NotifTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username='amir', email='a.ab@yahoo.com', password='1')

    def tearDown(self):
        User.objects.all().delete()
        ApiKey.objects.all().delete()

    def test_show_notif(self):
        api_key, created = ApiKey.objects.get_or_create(user=self.user)
        url = 'http://127.0.0.1:8000/api/v6/notif/?token=%s' % str(api_key.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_cotif_count(self):
        api_key, created = ApiKey.objects.get_or_create(user=self.user)
        url = 'http://127.0.0.1:8000/api/v6/notif/count/?token=%s' % str(api_key.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class PostTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username='amir', email='a.ab@yahoo.com', password='1')
        self.cat = Category.objects.create(title='sport',
                                           image='pin/blackhole/images/o/unittest_image.jpg')
        self.post = Post.objects.create(image="pin/blackhole/images/o/unittest_image.jpg",
                                        category=self.cat,
                                        user=self.user)

    def tearDown(self):
        User.objects.all().delete()
        ApiKey.objects.all().delete()
        Category.objects.all().delete()
        Post.objects.all().delete()

    def test_latest(self):
        url = 'http://127.0.0.1:8000/api/v6/post/latest/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_friends_post(self):
        api_key, created = ApiKey.objects.get_or_create(user=self.user)
        url = 'http://127.0.0.1:8000/api/v6/post/friends/?token=%s' % str(api_key.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_post_item(self):
        api_key, created = ApiKey.objects.get_or_create(user=self.user)
        url = 'http://127.0.0.1:8000/api/v6/post/item/%s/?token=%s' % (str(self.post.id), str(api_key.key))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_post_choice(self):
        response = self.client.get('http://127.0.0.1:8000/api/v6/post/choices/')
        self.assertEqual(response.status_code, 200)

    def test_search_post(self):
        response = self.client.get('http://127.0.0.1:8000/api/v6/post/search/?q=test')
        self.assertEqual(response.status_code, 200)

    def test_report_post(self):
        api_key, created = ApiKey.objects.get_or_create(user=self.user)
        url = 'http://127.0.0.1:8000/api/v6/post/report/%s/?token=%s' % (str(self.post.id), str(api_key.key))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_edit_post(self):
        api_key, created = ApiKey.objects.get_or_create(user=self.user)
        url = 'http://127.0.0.1:8000/api/v6/post/edit/%s/?token=%s' % (str(self.post.id), str(api_key.key))
        response = self.client.post(url, {'text': 'salam', 'url': 'http://www.google.com',
                                          'category': self.cat})
        self.assertEqual(response.status_code, 200)

    def test_send_post(self):

        file_path = os.path.join(settings.MEDIA_ROOT, 'pin/blackhole/images/o/unittest_image.jpg')
        myfile = open(file_path, 'r')
        api_key, created = ApiKey.objects.get_or_create(user=self.user)
        url = 'http://127.0.0.1:8000/api/v6/post/send/?token=%s' % str(api_key.key)
        response = self.client.post(url, {'image': myfile, 'description': 'salam',
                                          'url': 'http://www.google.com', 'category': self.cat})
        self.assertEqual(response.status_code, 200)

    def test_user_post(self):
        url = 'http://127.0.0.1:8000/api/v6/post/user/%s/' % str(self.user.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_related(self):
        url = 'http://wisgoon.com/api/v6/post/related/%s/' % str(self.post.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_promoted(self):
        api_key, created = ApiKey.objects.get_or_create(user=self.user)
        url = 'http://127.0.0.1:8000/api/v6/post/promoted/?token=%s' % str(api_key.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_hashtag(self):
        api_key, created = ApiKey.objects.get_or_create(user=self.user)
        url = 'http://127.0.0.1:8000/api/v6/post/hashtag/?token=%s&q=sport' % str(api_key.key)
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
