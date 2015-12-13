# coding: utf-8
import random
import time
import csv
import sys

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings

from tastypie.models import ApiKey

from user_profile.models import Profile

from pin.models import Post, Category, SubCategory, Comments, Follow
from pin.models_redis import LikesRedis

default_text = u'لورم ایپسوم متن ساختگی با تولید سادگی نامفهوم از صنعت چاپ و با استفاده از طراحان گرافیک است. چاپگرها و متون بلکه روزنامه و مجله در ستون و سطرآنچنان که لازم است و برای شرایط فعلی تکنولوژی مورد نیاز و کاربردهای متنوع با هدف بهبود ابزارهای کاربردی می باشد. کتابهای زیادی در شصت و سه درصد گذشته، حال و آینده شناخت فراوان جامعه و متخصصان را می طلبد تا با نرم افزارها شناخت بیشتری را برای طراحان رایانه ای علی الخصوص طراحان خلاقی و فرهنگ پیشرو در زبان فارسی ایجاد کرد. در این صورت می توان امید داشت که تمام و دشواری موجود در ارائه راهکارها و شرایط سخت تایپ به پایان رسد وزمان مورد نیاز شامل حروفچینی دستاوردهای اصلی و جوابگوی سوالات پیوسته اهل دنیای موجود طراحی اساسا مورد استفاده قرار گیرد.'

reload(sys)
sys.setdefaultencoding('utf8')


class Command(BaseCommand):
    def handle(self, *args, **options):

        # Create Users
        create_users(self)

        # Create Profile
        create_profile(self)

        # Create Category
        create_category(self)

        # Create Post
        create_post(self)

        # Create Like an Comments
        create_like_comment(self)

        # Create Follower
        create_test_follow(self)


def create_post(self):
    cnt_post = raw_input("How many posts you want to add?")
    cat_id = 0
    for index in range(1, int(cnt_post) + 1):
        filename = "post_%s.jpg" % str(random.randint(1, 50))
        user_id = random.randint(1, 200)
        try:
            post = Post()
            post.image = "v2/test_data/images/%s" % (filename)
            post.user_id = user_id
            post.timestamp = time.time()
            post.text = ''.join(default_text[random.randint(0, 100):random.randint(200, 600)])
            if cat_id == 44:
                cat_id = 1
            else:
                cat_id += 1
            post.category_id = cat_id
            post.save()
            self.stdout.write("post %s status: %s" % (str(post.id),
                                                      str(post.status)))

        except Exception as e:
            self.stdout.write(str(e))
            raise

    self.stdout.write("Finish Create Posts")


def create_like_comment(self):
    posts = Post.objects.all()
    for index, post in enumerate(posts):

        try:
            like_range = random.randint(0, 20)
            for a in range(like_range):
                text = ''.join(default_text[random.randint(0, 100):random.randint(200, 600)])
                user_id = random.randint(1, 200)
                LikesRedis(post_id=post.id)\
                    .like_or_dislike(user_id=user_id, post_owner=post.user_id)
            self.stdout.write("add %s like for post %s" % (str(like_range), str(post.id)))

            comment_range = random.randint(5, 20)
            for i in range(comment_range):
                user_id = random.randint(1, 200)
                text = ''.join(default_text[random.randint(0, 100):random.randint(200, 600)])
                comment = Comments()
                comment.object_pk_id = post.id
                comment.comment = text
                comment.user_id = user_id
                comment.save()

            self.stdout.write("add %s comment for post %s" % (str(comment_range), str(post.id)))

        except Exception as e:
            self.stdout.write(str(e))
            raise

    self.stdout.write("Finish Create Comments and likes")


def create_category(self):
    import json
    media_url = settings.MEDIA_ROOT
    path = "%s/v2/test_data/categories.json" % (media_url)

    try:
        with open(path) as data_file:
            data = json.load(data_file)
    except Exception as e:
        self.stdout.write(str(e))

    for obj in data:
        try:
            sub_cat = SubCategory.objects\
                .create(title=obj['name'],
                        image='v2/test_data/%s' % obj['img'])

            for cat in obj['childs']:
                cat_path = "v2/test_data/images/post_%s.jpg" % str(random.randint(1, 50))
                try:
                    Category.objects.create(title=cat, parent=sub_cat,
                                            image=cat_path)
                except Exception as e:
                    self.stdout.write(str(e))

        except Exception as e:
            self.stdout.write(str(e))

    self.stdout.write("Finish Create Category")


def create_users(self):
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
        self.stdout.write(str(e))
        raise

    for user in users_list:
        try:
            user = User.objects.create_user(user[0], user[1], user[2])
            ApiKey.objects.get_or_create(user=user)
        except Exception as e:
            self.stdout.write(str(e))

    self.stdout.write("Finish Create Users")


def create_test_follow(self):
    # cnt_follow = raw_input("How many follow you want to add?")
    for i in range(200):
        loop_count = random.randint(5, 30)

        for user in range(loop_count):
            try:
                Follow.objects.get_or_create(follower_id=i,
                                             following_id=random.randint(1, 200))
                self.stdout.write("Add %s Follow for user %s" % (str(user), str(i)))
            except Exception as e:
                self.stdout.write(str(e))
    self.stdout.write("finish Create Follower and following")


def create_profile(self):
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
        self.stdout.write(str(e))

    user_list = User.objects.order_by('-id')[:200]
    for index, user in enumerate(user_list):
        try:
            avatar_path = "v2/test_data/images/avatar/post_%s.jpg" % str(random.randint(1, 50))
            Profile.objects.filter(user=user)\
                .update(avatar=avatar_path, name=profile_list[index][0],
                        location=profile_list[index][1],
                        website=profile_list[index][2],
                        bio=profile_list[index][3], score=10000)

            self.stdout.write("user profile %s Updated" % user.username)
        except Exception as e:
            self.stdout.write(str(e))
