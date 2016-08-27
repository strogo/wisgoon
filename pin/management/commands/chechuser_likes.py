from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from pin.models import Post
from pin.models_redis import LikesRedis
# from django.db.models import Sum
# from datetime import datetime
# from user_profile.models import Profile


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = User.objects.get(id=264595)

        sum_lr = 0
        sum_mr = 0

        for p in Post.objects.filter(user=user):
            lr = LikesRedis(p.id).cntlike()
            lm = p.cnt_like

            sum_lr += lr
            sum_mr += lm

        print sum_lr, sum_mr

        # for user in users:
        #     print "user:", user.id
        #     posts = Post.objects.filter(user_id=user.id)\
        #         .aggregate(cnt_like=Sum('cnt_like'))

        #     if posts['cnt_like']:
        #         score = int(posts['cnt_like']) * 10
        #         Profile.objects.filter(user_id=user.id).update(score=score)
