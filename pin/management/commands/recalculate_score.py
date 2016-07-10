from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from pin.models import Post
from django.db.models import Sum
from datetime import datetime
from user_profile.models import Profile


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = User.objects.only('id').all()

        for user in users:
            posts = Post.objects.filter(user_id=user.id).aggregate(cnt_like=Sum('cnt_like'))

            if posts['cnt_like']:
                score = int(posts['cnt_like']) * 10
                Profile.objects.filter(user_id=user.id).update(score=score)
                print "recalculate user {} scores".format(user.id), datetime.now()
