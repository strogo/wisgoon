from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from pin.models import Post, Category, SubCategory, Comments, Follow
import random
from pin.models_redis import LikesRedis
import time
from tastypie.models import ApiKey


class Command(BaseCommand):
    def handle(self, *args, **options):
        word_file = "/usr/share/dict/words"
        words = open(word_file).read().splitlines()[100:200]
        sub_category = ['Sport', 'Political', 'Social', 'Cultural', 'Economic']
        category = ['football', 'volyball', 'doller', 'social', 'cultural', 'economic']

        # Create Users
        create_users(words)

        # Create Sub Category
        create_sub_cat(sub_category)

        # Create Category
        create_category(category)

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
            post.image = "pin/blackhole/images/o/%s" % (filename)
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


def create_category(category_list):
    for cat in category_list:
        try:
            Category.objects.create(title=cat,
                                    image='pin/blackhole/images/o/unittest_image.jpg')
        except Exception as e:
            print str(e)
            raise
    print "Finish Create Category"


def create_sub_cat(sub_category):
    for sub_cat in sub_category:
        try:
            SubCategory.objects.create(title=sub_cat,
                                       image='pin/blackhole/images/o/unittest_image.jpg')
        except Exception as e:
            print str(e)
            raise
    print "Finish Create Sub Category"


def create_users(usernames_list):
    for word in usernames_list:
        try:
            user = User.objects.create_user(word, '1', 'a.a@gmail.com')
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
