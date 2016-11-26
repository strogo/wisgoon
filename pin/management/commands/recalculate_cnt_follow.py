from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from pin.models import Follow
from user_profile.models import Profile


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = User.objects.only('id').all()

        for user in users:
            cnt_following = Follow.objects.filter(following_id=user.id).count()
            cnt_followers = Follow.objects.filter(follower_id=user.id).count()

            Profile.objects.filter(user_id=user.id)\
                .update(cnt_following=cnt_following,
                        cnt_followers=cnt_followers)
            print "recalculate user {} scores".format(user.id)
