import sys

from django.core.management.base import BaseCommand

from pin.models_graph import FollowUser
from pin.models import Follow

reload(sys)
sys.setdefaultencoding('utf8')


class Command(BaseCommand):
    def handle(self, *args, **options):
        limit = 0
        while True:
            follows = Follow.objects.filter(id__range=[limit, limit + 1000])
            if not follows:
                break

            for follow_obj in follows:
                try:
                    usr = follow_obj
                    FollowUser.get_or_create(start=usr.follower,
                                             end=usr.following,
                                             rel_type="follow")
                    self.stdout.write("relation {} created".format(follow_obj.id))
                except Exception as e:
                    print str(e)
            limit += 1001
            print limit
