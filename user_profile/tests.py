"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import unittest
from models import Profile, CreditLog
from django.contrib.auth.models import User


class ProfileTest(unittest.TestCase):

    def setUp(self):
        self.amir, created = User.objects\
            .get_or_create(username='amir', email='a.ab@yahoo.com', password='1')

    def tearDown(self):
        super(ProfileTest, self).tearDown()

    def test_create_profile(self):
        self.profile = Profile.objects.get(user=self.amir)
        self.assertIsInstance(self.profile, Profile)
