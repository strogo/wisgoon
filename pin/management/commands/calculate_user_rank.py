from django.core.management.base import BaseCommand
from user_profile.models import Profile
from django.db import transaction


class Command(BaseCommand):
    def handle(self, *args, **options):
        print "strating calculate user rank"
        offset = 0
        limit = 100
        status = True
        rank = 0
        trans = None
        while status:
            profiles = Profile.objects.only('user', 'rank')\
                .order_by("-score", "-cnt_post")[offset:offset + limit]

            if not profiles:
                status = False
            else:
                try:
                    with transaction.atomic():
                        for profile in profiles:
                            rank += 1
                            profile.rank = rank
                            profile.save()
                            trans = transaction.savepoint()
                        if trans:
                            transaction.savepoint_commit(trans)
                except Exception as e:
                    print str(e)

            offset = offset + limit
