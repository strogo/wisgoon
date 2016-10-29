from django.core.management.base import BaseCommand

from pin.models import Post
from django.contrib.auth.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = User.objects.only('id').filter(id__lt=1743656).order_by('-id')
        for user in users:
            cnt_post = Post.objects.only('id')\
                .filter(user_id=user.id)\
                .count()
            try:
                user.profile.cnt_post = cnt_post
                user.profile.save()
                print "user {} updated".format(user.id)
            except:
                pass
