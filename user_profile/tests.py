# coding: utf-8
import unittest
from models import Profile
from django.contrib.auth import get_user_model
User = get_user_model()


class ProfileTest(unittest.TestCase):

    def setUp(self):
        self.amir, created = User.objects\
            .get_or_create(username='amir', email='a.ab@yahoo.com', password='1')
        self.profile = Profile.objects.get(user=self.amir)

    def tearDown(self):
        super(ProfileTest, self).tearDown()

    def test_create_profile(self):
        self.profile.credit = 500
        self.profile.level = 1
        self.profile.save()

        self.assertIsInstance(self.profile, Profile)
        self.assertEqual(self.profile.credit, 500)
        self.assertEqual(self.profile.level, 1)
        self.assertFalse(self.profile.is_police())

    def test_inc_credit(self):
        self.profile.inc_credit(1000)
        self.profile = Profile.objects.get(user=self.amir)
        self.assertEqual(self.profile.credit, 1500)

    def dec_credit(self):
        self.profile.inc_credit(1000)
        self.profile = Profile.objects.get(user=self.amir)
        self.assertEqual(self.profile.credit, 500)

    def test_get_cnt_following(self):
        self.vahid, created = User.objects\
            .get_or_create(username='vahid', email='a.ac@yahoo.com', password='1')
        self.profile = Profile.objects.get(user=self.amir)

        self.assertEqual(self.profile.get_cnt_following(), 0)

    def test_get_cnt_followers(self):
        self.profile = Profile.objects.get(user=self.amir)

        self.assertEqual(self.profile.get_cnt_followers(), 0)
