from django.core.management.base import BaseCommand
from user_profile.models import Profile


class Command(BaseCommand):
    def handle(self, *args, **options):
        print "strating calculate user rank"
        offset = 0
        limit = 100
        status = True
        rank = 0
        while status:
            profiles = Profile.objects.only('user')\
                .order_by("-score", "-cnt_post")[offset:offset + limit]

            if not profiles:
                status = False

            for profile in profiles:
                rank += 1
                print profile.user.username, profile.score, rank
            offset = offset + limit
