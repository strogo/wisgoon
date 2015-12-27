# coding: utf-8
import random
import sys

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from tastypie.models import ApiKey

from pin.api6.tools import post_item_json
from pin.models import Post, Comments
from pin.models_redis import LikesRedis
from user_profile.models import Profile


reload(sys)
sys.setdefaultencoding('utf8')

default_text = u'لورم ایپسوم متن ساختگی با تولید سادگی نامفهوم از صنعت چاپ و با استفاده از طراحان گرافیک است. چاپگرها و متون بلکه روزنامه و مجله در ستون و سطرآنچنان که لازم است و برای شرایط فعلی تکنولوژی مورد نیاز و کاربردهای متنوع با هدف بهبود ابزارهای کاربردی می باشد. کتابهای زیادی در شصت و سه درصد گذشته، حال و آینده شناخت فراوان جامعه و متخصصان را می طلبد تا با نرم افزارها شناخت بیشتری را برای طراحان رایانه ای علی الخصوص طراحان خلاقی و فرهنگ پیشرو در زبان فارسی ایجاد کرد. در این صورت می توان امید داشت که تمام و دشواری موجود در ارائه راهکارها و شرایط سخت تایپ به پایان رسد وزمان مورد نیاز شامل حروفچینی دستاوردهای اصلی و جوابگوی سوالات پیوسته اهل دنیای موجود طراحی اساسا مورد استفاده قرار گیرد.'


class Command(BaseCommand):
    def handle(self, *args, **options):
        user_list = create_user(self)
        post = create_post(self)
        if post:
            post_item = post_item_json(post)

            edit_post(self, post)

            current_like = like_post(self, user_list, post)
            dislike_post(self, user_list, post)

            comment_ids, cnt_comment = add_comment(self, user_list, post)
            delete_comments(self, comment_ids)

            current_post = Post.objects.get(id=post.id)
            current_post_item = post_item_json(current_post)

            self.stdout.write('post_id: ' + str(post_item['id']))
            self.stdout.write('################')
            self.stdout.write('befor cnt_like: ' + str(post_item['cnt_like']))
            self.stdout.write('after 10 like cnt_like: ' + str(current_like))
            self.stdout.write('after 5 dislike cnt_like: ' + str(current_post_item['cnt_like']))
            self.stdout.write('################')
            self.stdout.write('befor cnt_comments: ' + str(post_item['cnt_comment']))
            self.stdout.write('after add 10 comment cnt_comments: ' + str(cnt_comment))
            self.stdout.write('after 5 remove cnt_comments: ' + str(current_post_item['cnt_comment']))
            self.stdout.write('################')
            self.stdout.write('befor url: ' + str(post_item['url']))
            self.stdout.write('after url: ' + str(current_post_item['url']))
            self.stdout.write('################')
            self.stdout.write('befor category_id: ' + str(post_item['category']['id']))
            self.stdout.write('after category_id: ' + str(current_post_item['category']['id']))
            self.stdout.write('################')
            self.stdout.write('befor text: ' + str(post_item['text']))
            self.stdout.write('after text: ' + str(current_post_item['text']))
        else:
            self.stdout.write('kjgkfjgkfj')


def create_user(self):
    user_list = ['amir1', 'vahid1', 'saeed', 'mohammad', 'majid',
                 'sadra', 'amirali', 'shohre', 'mohsen', 'amirhosein']
    create_user_list = []
    try:
        for user in user_list:
            email = user + '_ab@yahoo.com'
            user, created = User.objects.get_or_create(username=user,
                                                       email=email,
                                                       password='1')
            Profile.objects.filter(user=user).update(score=100000)
            ApiKey.objects.get_or_create(user=user)
            create_user_list.append(user)
    except Exception as e:
        error = "user exception:" + str(e)
        self.stdout.write(error)
        raise
    return create_user_list


def like_post(self, user_list, post):
    current_like = 0
    try:
        for user in user_list:
            like, dislike, current_like = LikesRedis(post_id=post.id)\
                .like_or_dislike(user_id=user.id, post_owner=post.user_id)
        return current_like
    except Exception as e:
        error = "like exception:" + str(e)
        self.stdout.write(error)
        raise


def dislike_post(self, user_list, post):
    current_like = 0
    try:
        for user in user_list[0:5]:
            like, dislike, current_like = LikesRedis(post_id=post.id)\
                .like_or_dislike(user_id=user.id, post_owner=post.user_id)
        return current_like
    except Exception as e:
        error = "dislike exception:" + str(e)
        self.stdout.write(error)
        raise


def add_comment(self, user_list, post):
    comment_ids_list = []
    cnt_comment = 0
    try:
        for user in user_list:
            text = ''.join(default_text[random.randint(0, 100):random.randint(200, 600)])
            comment = Comments()
            comment.object_pk_id = post.id
            comment.comment = text
            comment.user_id = user.id
            comment.save()
            comment_ids_list.append(comment.id)
            cnt_comment += 1
        return comment_ids_list, cnt_comment
    except Exception as e:
        error = "add_comment exception:" + str(e)
        self.stdout.write(error)
        raise


def delete_comments(self, comment_ids_list):
    try:
        comment_ids_list = [int(i) for i in comment_ids_list[0:5]]
        comments = Comments.objects.filter(id__in=comment_ids_list)
        for comment in comments:
            comment.delete()
    except Exception, e:
        error = "add_comment exception:" + str(e)
        self.stdout.write(error)
        raise


def create_post(self):
    import time

    filename = "post_%s.jpg" % str(random.randint(1, 100))

    post = None
    try:
        post = Post()
        post.image = "v2/test_data/images/%s" % (filename)
        post.user_id = random.randint(0, 100)
        post.timestamp = time.time()
        post.text = 'hiiiii'
        post.category_id = 1
        post.save()
        return post
    except Exception as e:
        error = "create post exception:" + str(e)
        self.stdout.write(error)
        raise


def edit_post(self, post):
    try:
        post.url = 'http://www.google.com'
        post.category_id = random.randint(1, 40)
        post.text = ''.join(default_text[random.randint(0, 100):random.randint(200, 600)])
        post.save()
    except Exception, e:
        error = "edit post exception:" + str(e)
        self.stdout.write(error)
        raise
