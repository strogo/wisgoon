"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from models import Post


class Test(TestCase):
    def setup(self):
        Post.objects.create(title="test")

    def test_basic_addition(self):
        post = Post.objects.get(title="test")
        self.assertEqual(post.id, 1)
