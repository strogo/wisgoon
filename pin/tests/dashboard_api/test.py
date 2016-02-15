# -*- coding: utf-8 -*-
import unittest
# import os
import json

from django.test import Client
from django.contrib.auth.models import User
# from django.conf import settings

from tastypie.models import ApiKey

from pin.models import Category, Post, Comments, Follow, Block
from pin.models_redis import LikesRedis


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
        self.follow1 = Follow.objects.create(follower=self.amir, following=self.vahid)
        self.follow2 = Follow.objects.create(follower=self.vahid, following=self.amir)

        # block user
        self.block1 = Block.objects.create(user=self.amir, blocked=self.saeed)
        self.block2 = Block.objects.create(user=self.vahid, blocked=self.saeed)

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

    def test_home_dashboard(self):
        response = self.client.get('http://127.0.0.1:8000/dashboard/api/home/',
                                   {"token": self.api_key.key})
        print self.api_key.key
        # Check that the response is 200 OK.
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['objects']['today_users'], 3)
        self.assertEqual(data['objects']['today_posts'], 2)
        self.assertEqual(data['objects']['today_likes'], 2)
        self.assertEqual(data['objects']['today_follow'], 2)
        self.assertEqual(data['objects']['today_blocks'], 2)
        self.assertEqual(data['objects']['today_view_pages'], 0)
        self.assertEqual(data['objects']['today_bills'], 0)
        self.assertEqual(data['objects']['today_comments'], 4)

    def tearDown(self):
        super(HomeTestCase, self).tearDown()


# class LogTestCase(unittest.TestCase):

#     def setUp(self):


#     def test_follow(self):
#         api_key, created = ApiKey.objects.get_or_create(user=self.amir)
#         response = self.client.get('http://127.0.0.1:8000/api/v6/auth/follow/',
#                                    {"token": api_key.key,
#                                     "user_id": self.vahid.id})
#         self.assertEqual(response.status_code, 200)

#     def test_unfollow(self):
#         api_key, created = ApiKey.objects.get_or_create(user=self.amir)
#         response = self.client.get('http://127.0.0.1:8000/api/v6/auth/unfollow/',
#                                    {"token": api_key.key,
#                                     "user_id": self.vahid.id})
#         self.assertEqual(response.status_code, 200)

#     def test_followers(self):
#         api_key, created = ApiKey.objects.get_or_create(user=self.amir)
#         url = 'http://127.0.0.1:8000/api/v6/auth/followers/%s/' % str(self.vahid.id)

#         response = self.client.get(url, {'token': api_key.key})
#         self.assertEqual(response.status_code, 200)

#     def test_following(self):
#         api_key, created = ApiKey.objects.get_or_create(user=self.amir)
#         url = 'http://127.0.0.1:8000/api/v6/auth/followers/%s/' % str(self.vahid.id)

#         response = self.client.get(url, {'token': api_key.key})
#         self.assertEqual(response.status_code, 200)

#     def test_profile(self):
#         api_key, created = ApiKey.objects.get_or_create(user=self.amir)
#         response = self.client.get('http://127.0.0.1:8000/api/v6/auth/user/%s/' % str(self.amir.id),
#                                    {"token": api_key.key})
#         self.assertEqual(response.status_code, 200)

#     def test_update_profile(self):
#         api_key, created = ApiKey.objects.get_or_create(user=self.amir)
#         url = 'http://127.0.0.1:8000/api/v6/auth/user/update/?token=%s' % str(api_key.key)
#         response = self.client.post(url, {'name': 'amir_ali',
#                                           'jens': 'M',
#                                           'bio': 'salam'})
#         self.assertEqual(response.status_code, 200)

#     def test_search_user(self):
#         api_key, created = ApiKey.objects.get_or_create(user=self.amir)
#         response = self.client.get('http://127.0.0.1:8000/api/v6/auth/user/search/',
#                                    {"token": api_key.key,
#                                     "q": 'vahid'})
#         self.assertEqual(response.status_code, 200)


# class CategoryTestCase(unittest.TestCase):

#     def setUp(self):
#         self.client = Client()
#         self.user, created = User.objects.get_or_create(username='amir', email='a.ab@yahoo.com', password='1')
#         self.cat, created = Category.objects.get_or_create(title='sport', image='/home/amir/Pictures/images.jpg')
#         # self.create_category()

#     def tearDown(self):
#         super(CategoryTestCase, self).tearDown()

#     def test_show_category(self):
#         api_key, created = ApiKey.objects.get_or_create(user=self.user)
#         response = self.client.get('http://127.0.0.1:8000/api/v6/category/%s/?token=%s' % (str(self.cat.id), str(api_key.key)))
#         self.assertEqual(response.status_code, 200)

#     def test_all_category(self):
#         api_key, created = ApiKey.objects.get_or_create(user=self.user)
#         response = self.client.get('http://127.0.0.1:8000/api/v6/category/all/?token=%s' % str(api_key.key))
#         self.assertEqual(response.status_code, 200)


# class CommentTestCase(unittest.TestCase):

#     def setUp(self):
#         self.client = Client()
#         self.user, created = User.objects.get_or_create(username='amir', email='a.ab@yahoo.com', password='1')
#         self.cat, created = Category.objects.get_or_create(title='sport',
#                                                            image='pin/blackhole/images/o/unittest_image.jpg')
#         self.post, created = Post.objects.get_or_create(image="pin/blackhole/images/o/unittest_image.jpg",
#                                                         category=self.cat,
#                                                         user=self.user)
#         self.comment, created = Comments.objects.get_or_create(comment='very nicee',
#                                                                object_pk=self.post,
#                                                                user=self.user)

#     def tearDown(self):
#         super(CommentTestCase, self).tearDown()

#     def test_post_comments(self):
#         url = 'http://127.0.0.1:8000/api/v6/comment/showComments/post/%s/' % str(self.post.id)
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)

#     def test_add_comment(self):
#         api_key, created = ApiKey.objects.get_or_create(user=self.user)
#         url = 'http://127.0.0.1:8000/api/v6/comment/add/post/%s/?token=%s' % (str(self.post.id), str(api_key.key))
#         response = self.client.post(url, {'comment': 'niceeee post'})
#         self.assertEqual(response.status_code, 200)

#     def test_delete_comment(self):
#         api_key, created = ApiKey.objects.get_or_create(user=self.user)
#         url = "http://127.0.0.1:8000/api/v6/comment/delete/%s/?token=%s" % (str(self.comment.id), str(api_key.key))
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)


# class LikeTestcase(unittest.TestCase):

#     def setUp(self):
#         self.client = Client()
#         self.user, created = User.objects.get_or_create(username='amir', email='a.ab@yahoo.com', password='1')
#         self.cat, created = Category.objects.get_or_create(title='sport',
#                                                            image='pin/blackhole/images/o/unittest_image.jpg')
#         self.post, created = Post.objects.get_or_create(image="pin/blackhole/images/o/unittest_image.jpg",
#                                                         category=self.cat,
#                                                         user=self.user)

#     def tearDown(self):
#         super(LikeTestcase, self).tearDown()

#     def test_like_post(self):
#         api_key, created = ApiKey.objects.get_or_create(user=self.user)
#         url = "http://127.0.0.1:8000/api/v6/like/post/%s/?token=%s" % (str(self.post.id), str(api_key.key))
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)

#     def test_post_likers(self):
#         url = "http://127.0.0.1:8000/api/v6/like/likers/post/%s/" % str(self.post.id)
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)


# class NotifTestCase(unittest.TestCase):

#     def setUp(self):
#         self.client = Client()
#         self.user, created = User.objects.get_or_create(username='amir', email='a.ab@yahoo.com', password='1')

#     def tearDown(self):
#         super(NotifTestCase, self).tearDown()

#     def test_show_notif(self):
#         api_key, created = ApiKey.objects.get_or_create(user=self.user)
#         url = 'http://127.0.0.1:8000/api/v6/notif/?token=%s' % str(api_key.key)
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)

#     def test_cotif_count(self):
#         api_key, created = ApiKey.objects.get_or_create(user=self.user)
#         url = 'http://127.0.0.1:8000/api/v6/notif/count/?token=%s' % str(api_key.key)
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)


# class PostTestCase(unittest.TestCase):

#     def setUp(self):
#         self.client = Client()
#         self.user, created = User.objects.get_or_create(username='amir', email='a.ab@yahoo.com', password='1')
#         self.cat, created = Category.objects.get_or_create(title='sport',
#                                                            image='pin/blackhole/images/o/unittest_image.jpg')
#         self.post, created = Post.objects.get_or_create(image="pin/blackhole/images/o/unittest_image.jpg",
#                                                         category=self.cat,
#                                                         user=self.user)

#     def tearDown(self):
#         super(PostTestCase, self).tearDown()

#     def test_latest(self):
#         url = 'http://127.0.0.1:8000/api/v6/post/latest/'
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)

#     def test_friends_post(self):
#         api_key, created = ApiKey.objects.get_or_create(user=self.user)
#         url = 'http://127.0.0.1:8000/api/v6/post/friends/?token=%s' % str(api_key.key)
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)

#     def test_post_item(self):
#         api_key, created = ApiKey.objects.get_or_create(user=self.user)
#         url = 'http://127.0.0.1:8000/api/v6/post/item/%s/?token=%s' % (str(self.post.id), str(api_key.key))
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)

#     def test_post_choice(self):
#         response = self.client.get('http://127.0.0.1:8000/api/v6/post/choices/')
#         self.assertEqual(response.status_code, 200)

#     def test_search_post(self):
#         response = self.client.get('http://127.0.0.1:8000/api/v6/post/search/?q=test')
#         self.assertEqual(response.status_code, 200)

#     def test_report_post(self):
#         api_key, created = ApiKey.objects.get_or_create(user=self.user)
#         url = 'http://127.0.0.1:8000/api/v6/post/report/%s/?token=%s' % (str(self.post.id), str(api_key.key))
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)

#     def test_edit_post(self):
#         api_key, created = ApiKey.objects.get_or_create(user=self.user)
#         url = 'http://127.0.0.1:8000/api/v6/post/edit/%s/?token=%s' % (str(self.post.id), str(api_key.key))
#         response = self.client.post(url, {'text': 'salam', 'url': 'http://www.google.com',
#                                           'category': self.cat})
#         self.assertEqual(response.status_code, 200)

#     def test_send_post(self):

#         file_path = os.path.join(settings.MEDIA_ROOT, 'pin/blackhole/images/o/unittest_image.jpg')
#         myfile = open(file_path, 'r')
#         api_key, created = ApiKey.objects.get_or_create(user=self.user)
#         url = 'http://127.0.0.1:8000/api/v6/post/send/?token=%s' % str(api_key.key)
#         response = self.client.post(url, {'image': myfile, 'description': 'salam',
#                                           'url': 'http://www.google.com', 'category': self.cat})
#         self.assertEqual(response.status_code, 200)

#     def test_user_post(self):
#         url = 'http://127.0.0.1:8000/api/v6/post/user/%s/' % str(self.user.id)
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)

#     def test_related(self):
#         url = 'http://wisgoon.com/api/v6/post/related/%s/' % str(self.post.id)
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)

#     def test_promoted(self):
#         api_key, created = ApiKey.objects.get_or_create(user=self.user)
#         url = 'http://127.0.0.1:8000/api/v6/post/promoted/?token=%s' % str(api_key.key)
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)

#     def test_hashtag(self):
#         api_key, created = ApiKey.objects.get_or_create(user=self.user)
#         url = 'http://127.0.0.1:8000/api/v6/post/hashtag/?token=%s&q=sport' % str(api_key.key)
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)

# if __name__ == '__main__':
#     unittest.main()
