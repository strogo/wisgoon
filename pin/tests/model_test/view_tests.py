# -*- coding: utf-8 -*-
from pin.models import *
import unittest
from user_profile.models import Profile
from django.core.cache import cache


class SubCategoryTestCase(unittest.TestCase):

    def setUp(self):
        self.cat = Category.objects.create(title='sport',
                                           image='pin/blackhole/images/o/unittest_image.jpg')

    def tearDown(self):
        super(SubCategoryTestCase, self).tearDown()

    def test_admin_image(self):
        self.assertEqual(self.cat.admin_image(), '<img src="/media/%s" />' % self.image)

    def test_update_category(self):
        self.cat.title = 'social'
        self.cat.save()
        self.assertEqual(self.cat.title, 'social')


class AdTestCase(unittest.TestCase):

    def setUp(self):
        self.user, created = User.objects.get_or_create(username='amir', email='a.ab@yahoo.com', password='1')
        self.user2, created = User.objects.get_or_create(username='vahid', email='a.abc@yahoo.com', password='1')
        self.cat, created = Category.objects.get_or_create(title='sport',
                                                           image='pin/blackhole/images/o/unittest_image.jpg')
        self.post, created = Post.objects.get_or_create(image="pin/blackhole/images/o/unittest_image.jpg",
                                                        category=self.cat,
                                                        user=self.user)
        self.ad, created = Ad.objects.get_or_create(image="pin/blackhole/images/o/unittest_image.jpg",
                                                    owner=self.post.user, user=self.user2, ended=1,
                                                    cnt_view=12, post=self.post, ads_type=Ad.TYPE_1000_USER)

    def tearDown(self):
        super(AdTestCase, self).tearDown()

    def test_get_cnt_view(self):
        self.assertEqual(self.ad.get_cnt_view(), 12)

    # def test_get_ad(self):
    #     self.assertEqual(Ad.get_ad(self.user.id), 12)

    def test_save(self):
        self.assertEqual(self.ad.owner, self.post.user)


class CategoryTestCase(unittest.TestCase):

    def setUp(self):
        self.user, created = User.objects.get_or_create(username='amir', email='a.ab@yahoo.com', password='1')
        self.cat, created = Category.objects.get_or_create(title='sport',
                                                           image='pin/blackhole/images/o/unittest_image.jpg')

    def tearDown(self):
        super(AdTestCase, self).tearDown()

    def test_admin_image(self):
        self.assertEqual(self.ad.test_admin_image(), '<img src="/media/%s" />' % self.image)

    # def test_get_json(self):
    #     self.assertEqual(Ad.get_json(self.cat.id), '')


class PostTestCase(unittest.TestCase):

    def setUp(self):
        self.user, created = User.objects.get_or_create(username='amir', email='a.ab@yahoo.com', password='1')
        self.cat, created = Category.objects.get_or_create(title='sport',
                                                           image='pin/blackhole/images/o/unittest_image.jpg')
        self.post, created = Post.objects.get_or_create(image="pin/blackhole/images/o/unittest_image.jpg",
                                                        category=self.cat,
                                                        user=self.user)
        try:
            self.score = Profile.objects.only('score').get(user_id=self.user_id).score
        except Profile.DoesNotExist:
            self.profile = Profile.objects.create(user_id=user_id)
            self.score = self.profile.score

    def tearDown(self):
        super(AdTestCase, self).tearDown()

    # def test_get_username(self):
    #     self.assertEqual(self.post.get_pages(), '')

    def test_get_username(self):
        self.assertEqual(self.post.get_username(), self.user.username)

    def test_get_profile_score(self):
        self.assertEqual(self.post.get_profile_score(), self.score)

    def test_is_pending(self):
        self.assertEqual(self.post.is_pending(), False)

    def test_get_tags(self):
        self.assertEqual(self.post.get_tags(), None)

    def test_get_image_sizes(self):
        self.assertEqual(self.post.get_image_sizes(), {"width": self.post.width,
                                                       "height": self.post.height})

    def test_clear_cache(self):
        cname = "pmeta_%d_236" % int(self.post.id)
        self.post.clear_cache()
        has_key = cname in cache
        self.assertEqual(has_key, False)

    def test_get_image_236(self):
        result = {'h': 74,
                  'hw': '74x236',
                  'url': u'http://127.0.0.1:8000/media/pin/blackhole/images/o/236x74_unittest_image.jpg'}

        self.assertEqual(self.post.get_image_236, result)

    def test_get_image_500(self):
        result = {'h': 157, 'hw': '157x500',
                  'url': u'http://127.0.0.1:8000/media/pin/blackhole/images/o/500x157_unittest_image.jpg'}
        self.assertEqual(self.post.get_image_236, result)

    def test_delete(self):
        self.assertEqual(self.post.id, 1)


if __name__ == '__main__':
    unittest.main()
