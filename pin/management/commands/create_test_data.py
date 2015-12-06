# coding: utf-8
import random
import time
import csv
import sys

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings

from tastypie.models import ApiKey

from pin.models import Post, Category, SubCategory, Comments, Follow
from pin.models_redis import LikesRedis

reload(sys)
sys.setdefaultencoding('utf8')


class Command(BaseCommand):
    def handle(self, *args, **options):

        # Create Users
        create_users()

        # Create Profile
        create_profile()

        # Create Sub Category
        create_sub_cat()

        # Create Category
        create_category()

        # Create Post
        create_post(1000)

        # Create Like an Comments
        create_like_comment()

        # Create Follower
        create_test_follow()


def create_post(cnt_post):
    for index in xrange(1, cnt_post + 1):
        filename = "post_%s.jpg" % str(random.randint(1, 50))
        try:
            post = Post()
            post.image = "v2/test_data/%s" % (filename)
            post.user_id = random.randint(1, 100)
            post.timestamp = time.time()
            post.text = 'slaaaaam'
            post.category_id = random.randint(1, 6)
            post.save()
            print "Post %s Created" % str(index)

        except Exception as e:
            print str(e)
            raise
    print "Finish Create Posts"


def create_like_comment():
    posts = Post.objects.all()
    comment_list = []
    for index, post in enumerate(posts):
        text = "String number %s" % index
        user_id = random.randint(1, 100)

        like, dislike, current_like = LikesRedis(post_id=post.id)\
            .like_or_dislike(user_id=user_id, post_owner=post.user_id)

        try:
            comment_list.append(Comments(object_pk=post, comment=text, user_id=user_id))
            print "comment %s append to list" % index
        except Exception as e:
            print str(e)
            raise
    try:
        Comments.objects.bulk_create(comment_list)
    except Exception as e:
        print str(e)
        raise
    print "Finish Create Commnts and likes"


def create_category():
    category_list = ['football', 'volyball', 'doller', 'social', 'cultural', 'economic']
    for cat in category_list:
        try:
            Category.objects.create(title=cat,
                                    image='v2/test_data/unittest_image.jpg')
        except Exception as e:
            print str(e)
            raise
    print "Finish Create Category"


def create_sub_cat():
    sub_category = ['Sport', 'Political', 'Social', 'Cultural', 'Economic']
    for sub_cat in sub_category:
        try:
            SubCategory.objects.create(title=sub_cat,
                                       image='v2/test_data/unittest_image.jpg')
        except Exception as e:
            print str(e)
            raise
    print "Finish Create Sub Category"


def create_users():
    users_list = []
    media_url = settings.MEDIA_ROOT
    path = "%s/v2/test_data/auth_user.csv" % (media_url)
    try:
        f = open(path, 'rb')
        reader = csv.reader(f)
        for row in reader:
            users_list.append([row[1], '1', row[4]])
        f.close()
    except Exception as e:
        print str(e)
        raise

    for user in users_list:
        try:
            user = User.objects.create_user(user[0], user[1], user[2])
            ApiKey.objects.get_or_create(user=user)
        except Exception as e:
            print str(e)
            raise
    print "Finish Create Users"


def create_test_follow():
    for i in xrange(1, 51):
        try:
            Follow.objects.get_or_create(follower_id=i, following_id=i + 3)
            Follow.objects.get_or_create(follower_id=i + 3, following_id=i)
            print "Add Follower"
        except Exception as e:
            print str(e)
            raise
    print "finish Create Follower and following"


def create_profile():
    profile_list = []
    media_url = settings.MEDIA_ROOT
    path = "%s/v2/test_data/user_profile_profile.csv" % (media_url)
    try:
        f = open(path, 'rb')
        reader = csv.reader(f)
        for row in reader:
            profile_list.append([row[1], row[2], row[3], row[4]])
        f.close()
    except Exception as e:
        print str(e)
        raise

    user_list = User.objects.exclude(username='root').order_by('-id')
    for index, user in enumerate(user_list):
        try:
            if profile_list[index][0]:
                user.profile.name = profile_list[index][0]

            if profile_list[index][1]:
                user.profile.location = profile_list[index][1]

            if profile_list[index][2]:
                user.profile.website = profile_list[index][2]

            if profile_list[index][3]:
                user.profile.bio = profile_list[index][3]
            user.profile.save()
            print "user profile %s Updated" % user.username
        except Exception as e:
            print str(e)
            raise
    print "Finish Create Users"
