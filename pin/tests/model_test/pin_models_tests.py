# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from pin.models import (Category, Post, Ad, Follow, Likes, Notifbar, Notif,
                        Comments, Comments_score, Report)
from django.test import TestCase
from user_profile.models import Profile
from django.core.cache import cache


class SubCategoryTestCase(TestCase):

    def setUp(self):
        self.cat, created = Category.objects.get_or_create(title='sport',
                                                           image='pin/blackhole/images/o/unittest_image.jpg')

    def tearDown(self):
        super(SubCategoryTestCase, self).tearDown()

    def test_admin_image(self):
        self.assertEqual(self.cat.admin_image(), '<img src="/media/%s" />' % self.cat.image)

    def test_update_category(self):
        self.cat.title = 'social'
        self.cat.save()
        self.assertEqual(self.cat.title, 'social')


class AdTestCase(TestCase):

    def setUp(self):
        self.user, created = User.objects.get_or_create(username='amir', email='a.ab@yahoo.com', password='1')
        self.user2, created = User.objects.get_or_create(username='vahid', email='a.abc@yahoo.com', password='1')
        self.cat, created = Category.objects.get_or_create(title='sport',
                                                           image='pin/blackhole/images/o/unittest_image.jpg')
        self.post, created = Post.objects.get_or_create(image="pin/blackhole/images/o/unittest_image.jpg",
                                                        category=self.cat,
                                                        user=self.user)
        self.ad, created = Ad.objects.get_or_create(owner=self.post.user, user=self.user2,
                                                    ended=1, cnt_view=12, post=self.post,
                                                    ads_type=Ad.TYPE_1000_USER)

    def tearDown(self):
        super(AdTestCase, self).tearDown()

    def test_get_cnt_view(self):
        self.assertEqual(self.ad.get_cnt_view(), 12)

    # def test_get_ad(self):
    #     self.assertEqual(Ad.get_ad(self.user.id), 12)

    def test_save(self):
        self.assertEqual(self.ad.owner, self.post.user)


class CategoryTestCase(TestCase):

    def setUp(self):
        self.user, created = User.objects.get_or_create(username='amir', email='a.ab@yahoo.com', password='1')
        self.cat, created = Category.objects.get_or_create(title='sport',
                                                           image='pin/blackhole/images/o/unittest_image.jpg')

    def tearDown(self):
        super(CategoryTestCase, self).tearDown()

    def test_admin_image(self):
        self.assertEqual(self.cat.admin_image(), '<img src="/media/%s" />' % self.cat.image)

    # def test_get_json(self):
    #     self.assertEqual(Ad.get_json(self.cat.id), '')


class PostTestCase(TestCase):

    def setUp(self):
        self.user, created = User.objects.get_or_create(username='amir', email='a.ab@yahoo.com', password='1')
        self.cat, created = Category.objects.get_or_create(title='sport',
                                                           image='pin/blackhole/images/o/unittest_image.jpg')
        self.post, created = Post.objects.get_or_create(image="pin/blackhole/images/o/unittest_image.jpg",
                                                        category=self.cat,
                                                        user=self.user)
        try:
            self.score = Profile.objects.only('score').get(user_id=self.user.id).score
        except Profile.DoesNotExist:
            self.profile = Profile.objects.create(user_id=self.user.id)
            self.score = self.profile.score

    def tearDown(self):
        super(PostTestCase, self).tearDown()

    # def test_get_username(self):
    #     self.assertEqual(self.post.get_pages(), '')

    def test_get_username(self):
        self.assertEqual(self.post.get_username(), self.user.username)

    def test_get_profile_score(self):
        self.assertEqual(self.post.get_profile_score(), self.score)

    def test_is_pending(self):
        self.assertEqual(self.post.is_pending(), False)

    def test_get_tags(self):
        self.assertEqual(self.post.get_tags(), [])

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

        self.assertEqual(self.post.get_image_236(), result)

    def test_get_image_500(self):
        result = {'h': 157, 'hw': '157x500',
                  'url': u'http://127.0.0.1:8000/media/pin/blackhole/images/o/500x157_unittest_image.jpg'}
        self.assertEqual(self.post.get_image_500(), result)

    def test_delete(self):
        self.delete = self.post.delete()
        self.assertEqual(self.delete, None)

    def test_cnt_likes(self):
        self.assertIsNotNone(self.post.cnt_likes())

    def test_cnt_comments(self):
        self.assertIsNotNone(self.post.cnt_comments())

    def test_home_latest(self):
        self.assertListEqual(Post.home_latest(), ['3', '1', '7', '4', '3', '8', '9', '10', '13', '12', '11', '14', '16', '15', '18', '19', '17', '20', '21', '33'])

    def test_latest(self):
        self.assertListEqual(Post.latest(), ['23', '4', '2'])

    def test_last_likes(self):
        self.assertIsNotNone(Post.last_likes())


class FollowTestCase(TestCase):

    def setUp(self):
        self.amir, created = User.objects.get_or_create(username='amir', email='a.ab@yahoo.com', password='1')
        self.vahid, created = User.objects.get_or_create(username='vahid', email='a.abc@yahoo.com', password='1')

    def tearDown(self):
        super(FollowTestCase, self).tearDown()

    def test_get_follow_status(self):
        Follow.objects.get_or_create(follower_id=self.amir.id, following_id=self.vahid.id)
        self.assertTrue(Follow.get_follow_status(self.amir.id, self.vahid.id))

    def test_delete(self):
        self.follow, created = Follow.objects.get_or_create(following_id=self.vahid.id, follower_id=self.amir.id)
        self.delete = self.follow.delete()
        self.assertEqual(self.delete, None)


class LikesTestCase(TestCase):

    def setUp(self):
        self.user, created = User.objects.get_or_create(username='amir', email='a.ab@yahoo.com', password='1')
        self.cat, created = Category.objects.get_or_create(title='sport',
                                                           image='pin/blackhole/images/o/unittest_image.jpg')
        self.post, created = Post.objects.get_or_create(image="pin/blackhole/images/o/unittest_image.jpg",
                                                        category=self.cat,
                                                        user=self.user)

    def tearDown(self):
        super(LikesTestCase, self).tearDown()

    def test_create_likes(self):
        self.like = Likes(user_id=self.user.id, post_id=self.post.id)
        self.assertIsInstance(self.like, Likes)

    def test_delete(self):
        self.like, created = Likes.objects.get_or_create(user_id=self.user.id, post_id=self.post.id)
        self.delete = self.like.delete()
        self.assertEqual(self.delete, None)


class NotifbarTestCase(TestCase):

    def setUp(self):
        self.amir, created = User.objects.get_or_create(username='amir', email='a.ab@yahoo.com', password='1')
        self.vahid, created = User.objects.get_or_create(username='vahid', email='a.abc@yahoo.com', password='1')
        self.cat, created = Category.objects.get_or_create(title='sport',
                                                           image='pin/blackhole/images/o/unittest_image.jpg')
        self.post, created = Post.objects.get_or_create(image="pin/blackhole/images/o/unittest_image.jpg",
                                                        category=self.cat,
                                                        user=self.vahid)

    def tearDown(self):
        super(NotifbarTestCase, self).tearDown()

    def test_create_notif_bar(self):
        self.notif = Notifbar(post=self.post, actor=self.amir, user=self.vahid, type=Notifbar.LIKE)
        self.assertIsInstance(self.notif, Notifbar)


class NotifTestCase(TestCase):

    def setUp(self):
        self.amir, created = User.objects.get_or_create(username='amir', email='a.ab@yahoo.com', password='1')
        self.vahid, created = User.objects.get_or_create(username='vahid', email='a.abc@yahoo.com', password='1')
        self.cat, created = Category.objects.get_or_create(title='sport',
                                                           image='pin/blackhole/images/o/unittest_image.jpg')
        self.post, created = Post.objects.get_or_create(image="pin/blackhole/images/o/unittest_image.jpg",
                                                        category=self.cat,
                                                        user=self.vahid)

    def tearDown(self):
        super(NotifTestCase, self).tearDown()

    def test_create_notif_bar(self):
        self.notif = Notif(post=self.post, user=self.vahid, text='salam')
        self.assertIsInstance(self.notif, Notif)


class CommentsTestCase(TestCase):

    def setUp(self):
        self.amir, created = User.objects.get_or_create(username='amir', email='a.ab@yahoo.com', password='1')
        self.cat, created = Category.objects.get_or_create(title='sport',
                                                           image='pin/blackhole/images/o/unittest_image.jpg')
        self.post, created = Post.objects.get_or_create(image="pin/blackhole/images/o/unittest_image.jpg",
                                                        category=self.cat,
                                                        user=self.amir)

    def tearDown(self):
        super(CommentsTestCase, self).tearDown()

    def test_create_comment(self):
        self.comment = Comments(comment='kksjdksjdksdkjs', object_pk=self.post, user=self.amir)
        self.assertIsInstance(self.comment, Comments)

    def test_get_username(self):
        self.comment, created = Comments.objects.get_or_create(comment='kksjdksjdksdkjs',
                                                               object_pk=self.post,
                                                               user=self.amir)
        self.assertEqual(self.comment.get_username(), self.amir.username)

    def test_delete(self):
        self.comment, created = Comments.objects.get_or_create(comment='kksjdksjdksdkjs',
                                                               object_pk=self.post,
                                                               user=self.amir)
        self.delete = self.comment.delete()
        self.assertEqual(self.delete, None)


class CommentsScoreTestCase(TestCase):

    def setUp(self):
        self.amir, created = User.objects.get_or_create(username='amir', email='a.ab@yahoo.com', password='1')
        self.cat, created = Category.objects.get_or_create(title='sport',
                                                           image='pin/blackhole/images/o/unittest_image.jpg')
        self.post, created = Post.objects.get_or_create(image="pin/blackhole/images/o/unittest_image.jpg",
                                                        category=self.cat,
                                                        user=self.amir)
        self.comment, created = Comments.objects.get_or_create(comment='kksjdksjdksdkjs',
                                                               object_pk=self.post,
                                                               user=self.amir)

    def tearDown(self):
        super(CommentsScoreTestCase, self).tearDown()

    def test_create_comment_score(self):
        self.score = Comments_score(user=self.amir, comment=self.comment, score=100)
        self.assertIsInstance(self.score, Comments_score)


class ClassReportTestCase(TestCase):

    def setUp(self):
        self.amir, created = User.objects.get_or_create(username='amir', email='a.ab@yahoo.com', password='1')
        self.vahid, created = User.objects.get_or_create(username='vahid', email='a.abc@yahoo.com', password='1')

        self.cat, created = Category.objects.get_or_create(title='sport',
                                                           image='pin/blackhole/images/o/unittest_image.jpg')
        self.post, created = Post.objects.get_or_create(image="pin/blackhole/images/o/unittest_image.jpg",
                                                        category=self.cat,
                                                        user=self.amir)

    def tearDown(self):
        super(ClassReportTestCase, self).tearDown()

    def test_create(self):
        self.report = Report(user=self.vahid, post=self.post)
        self.assertIsInstance(self.report, Report)

# if __name__ == '__main__':
#     TestCase.main()
