# -*- coding: utf-8 -*-
import unittest
# import os
import json

from django.test import Client
from django.contrib.auth.models import User
from django.test.utils import override_settings

# from django.conf import settings

from tastypie.models import ApiKey

from pin.models import Category, Post, Comments, Follow, Block, Report
from pin.models_redis import LikesRedis

from user_profile.models import Profile


class HomeTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()

        # add user
        self.amir, created = User.objects\
            .get_or_create(username='amir', email='a.ab@yahoo.com',
                           password='1', is_superuser=True, is_staff=True,
                           is_active=True)

        self.vahid, created = User.objects\
            .get_or_create(username='vahid', email='v.abc@yahoo.com', password='1')

        self.saeed, created = User.objects\
            .get_or_create(username='saeed', email='s.abc@yahoo.com', password='1')

        # add api key
        self.api_key, created = ApiKey.objects.get_or_create(user=self.amir)

        # add category
        self.cat, created = Category.objects\
            .get_or_create(title='sport',
                           image='/home/amir/Pictures/images.jpg')
        # add posts
        self.post1, created = Post.objects\
            .get_or_create(image="pin/blackhole/images/o/unittest_image.jpg",
                           category=self.cat,
                           user=self.amir)

        self.post2, created = Post.objects\
            .get_or_create(image="pin/blackhole/images/o/unittest_image.jpg",
                           category=self.cat,
                           user=self.vahid)
        # follow user

        self.follow1 = Follow.objects.create(follower=self.amir,
                                             following=self.vahid)
        self.follow2 = Follow.objects.create(follower=self.vahid,
                                             following=self.amir)
        # block user
        self.block1 = Block.block_user(user_id=self.amir.id,
                                       blocked_id=self.saeed.id)
        self.block2 = Block.block_user(user_id=self.vahid.id,
                                       blocked_id=self.saeed.id)
        # add comment
        self.comment1 = Comments.objects.create(object_pk=self.post1,
                                                comment='salam',
                                                user_id=self.amir.id)
        self.comment2 = Comments.objects.create(object_pk=self.post1,
                                                comment='salam',
                                                user_id=self.vahid.id)
        self.comment3 = Comments.objects.create(object_pk=self.post2,
                                                comment='salam',
                                                user_id=self.amir.id)
        self.comment4 = Comments.objects.create(object_pk=self.post2,
                                                comment='salam',
                                                user_id=self.vahid.id)
        # like post
        like, dislike, current_like = LikesRedis(post_id=self.post1.id)\
            .like_or_dislike(user_id=self.amir.id,
                             post_owner=self.post1.user_id,
                             category=self.post1.category_id)

        like, dislike, current_like = LikesRedis(post_id=self.post2.id)\
            .like_or_dislike(user_id=self.vahid.id,
                             post_owner=self.post2.user_id,
                             category=self.post2.category_id)

    @override_settings(DEBUG=True)
    def test_home_dashboard(self):
        url = 'http://127.0.0.1:8000/dashboard/api/home/?token='
        response = self.client.get(url, {'token': self.api_key.key})

        # Check that the response is 200 OK.
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['objects']['today_users']['cnt_users'], 3)
        self.assertEqual(data['objects']['today_posts']['cnt_posts'], 2)
        self.assertEqual(data['objects']['today_likes']['cnt_likes'], 2)
        self.assertEqual(data['objects']['today_follow']['cnt_follows'], 2)
        self.assertEqual(data['objects']['today_blocks']['cnt_blocks'], 2)
        self.assertEqual(data['objects']['today_view_pages']['cnt_view_pages'], 0)
        self.assertEqual(data['objects']['today_bills']['cnt_bills'], 0)
        self.assertEqual(data['objects']['today_comments']['cnt_comments'], 4)

    def tearDown(self):
        super(HomeTestCase, self).tearDown()


class PostTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        # add user
        self.amir, created = User.objects\
            .get_or_create(username='amir', email='a.ab@yahoo.com',
                           password='1', is_superuser=True, is_staff=True,
                           is_active=True)

        self.vahid, created = User.objects\
            .get_or_create(username='vahid', email='v.abc@yahoo.com',
                           password='1')

        self.saeed, created = User.objects\
            .get_or_create(username='saeed', email='s.abc@yahoo.com',
                           password='1')
        # add profile
        self.profile, created = Profile.objects\
            .get_or_create(user=self.amir, name=self.amir.username)

        # add api key
        self.api_key, created = ApiKey.objects.get_or_create(user=self.amir)

        # add category
        self.cat, created = Category.objects\
            .get_or_create(title='sport',
                           image='/home/amir/Pictures/images.jpg')
        # add posts
        self.post1, created = Post.objects\
            .get_or_create(image="pin/blackhole/images/o/unittest_image.jpg",
                           category=self.cat,
                           user=self.amir)

        self.post2, created = Post.objects\
            .get_or_create(image="pin/blackhole/images/o/unittest_image.jpg",
                           category=self.cat,
                           user=self.vahid)
        # add report post
        self.report1, created = Report.objects.create(user_id=self.vahid.id,
                                                      post=self.post1)
        self.report2, created = Report.objects.create(user_id=self.amir.id,
                                                      post=self.post2)

    @override_settings(DEBUG=True)
    def test_reported(self):
        url = 'http://127.0.0.1:8000/dashboard/api/post/reported/'
        response = self.client.get(url, {'token': self.api_key.key})

        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['objects'][0]['cnt_report'], 1)
        self.assertEqual(data['objects'][2]['cnt_report'], 1)

    @override_settings(DEBUG=True)
    def test_post_reporter_user(self):
        url = 'http://127.0.0.1:8000/dashboard/api/post/reporters/{}'\
            .format(str(self.post1.id))
        response = self.client.get(url, {'token': self.api_key.key})

        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['objects']['reporter']['username'], 'amir')

    @override_settings(DEBUG=True)
    def test_post_user_details(self):
        url = 'http://127.0.0.1:8000/dashboard/api/post/user/{}'\
            .format(str(self.amir.id))
        response = self.client.get(url, {'token': self.api_key.key})

        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['profile']['name'], 'amir')

    @override_settings(DEBUG=True)
    def test_enable_ads(self):
        url = 'http://127.0.0.1:8000/dashboard/api/post/enableAds/'
        response = self.client.get(url, {'token': self.api_key.key})

        self.assertEqual(response.status_code, 200)

    @override_settings(DEBUG=True)
    def test_disable_ads(self):
        url = 'http://127.0.0.1:8000/dashboard/api/post/disableAds/'
        response = self.client.get(url, {'token': self.api_key.key})

        self.assertEqual(response.status_code, 200)

    @override_settings(DEBUG=True)
    def test_show_ads(self):
        url = 'http://127.0.0.1:8000/dashboard/api/post/showAds/'
        response = self.client.get(url, {'token': self.api_key.key,
                                         'date': '1455104405'})

        self.assertEqual(response.status_code, 200)

    @override_settings(DEBUG=True)
    def test_post_of_category(self):
        url = 'http://127.0.0.1:8000/dashboard/api/post/category/chart/{}/'\
            .format(self.cat.title)
        response = self.client.get(url, {'token': self.api_key.key})

        self.assertEqual(response.status_code, 200)

    @override_settings(DEBUG=True)
    def test_post_of_sub_category(self):
        url = 'http://127.0.0.1:8000/dashboard/api/post/subcategory/chart/'
        response = self.client.get(url, {'token': self.api_key.key})

        self.assertEqual(response.status_code, 200)

    @override_settings(DEBUG=True)
    def test_delete_post(self):
        url = 'http://127.0.0.1:8000/dashboard/api/post/delete/?token={}'\
            .format(self.api_key.key)
        response = self.client.post(url, {'post_ids': self.post1.id})

        self.assertEqual(response.status_code, 200)

    @override_settings(DEBUG=True)
    def test_undo_report(self):
        url = 'http://127.0.0.1:8000/dashboard/api/post/report/undo/?token='\
            .format(self.api_key.key)
        response = self.client.post(url, {'post_ids': self.post2.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.post2.report, 0)

    def tearDown(self):
        super(PostTestCase, self).tearDown()


class UserTestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        # add user
        self.amir, created = User.objects\
            .get_or_create(username='amir', email='a.ab@yahoo.com',
                           password='1', is_superuser=True, is_staff=True,
                           is_active=True)

        self.vahid, created = User.objects\
            .get_or_create(username='vahid', email='v.abc@yahoo.com',
                           password='1')
        # add profile
        self.profile, created = Profile.objects\
            .get_or_create(user=self.amir, name=self.amir.username)

        # add api key
        self.api_key, created = ApiKey.objects.get_or_create(user=self.amir)

    @override_settings(DEBUG=True)
    def test_search_user(self):
        url = 'http://127.0.0.1:8000/dashboard/api/user/search/'
        response = self.client.get(url, {'token': self.api_key.key,
                                         'q': self.amir.username})

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['objects'][0]['username'], 'amir')

    @override_settings(DEBUG=True)
    def test_user_details(self):
        url = 'http://127.0.0.1:8000/dashboard/api/user/details/{}/'\
            .format(self.amir.id)
        response = self.client.get(url, {'token': self.api_key.key})

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['objects']['profile']['name'], 'amir')

    @override_settings(DEBUG=True)
    def test_change_status_user(self):
        url = 'http://127.0.0.1:8000/dashboard/api/user/changeStatus/?token={}'\
            .format(self.api_key.key)
        response = self.client.post(url, {'activeId': self.vahid.id,
                                          'activeStatus': 0,
                                          'description1': 'test'})

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['profile']['name'], 'vahid')
        self.assertEqual(data['profile']['user_active'], 0)

    @override_settings(DEBUG=True)
    def test_banned_profile(self):
        url = 'http://127.0.0.1:8000/dashboard/api/user/bannedProfile/?token={}'\
            .format(self.api_key.key)
        response = self.client.post(url, {'profileBanId': self.profile.id,
                                          'profileBanstatus': 0,
                                          'description2': 'test'})

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['profile']['name'], 'amir')
        self.assertEqual(data['profile']['userBanne_profile'], 0)

    # @override_settings(DEBUG=True)
    # def test_banned_imei(self):
    #     url = 'http://127.0.0.1:8000/dashboard/api/user/bannedImei/?token={}'\
    #         .format(self.api_key.key)
    #     response = self.client.post(url, {'status': 0,
    #                                       'description3': 'salam',
    #                                       'imei': '123456789'})

        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        super(UserTestCase, self).tearDown()
