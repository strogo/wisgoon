import sys

from django.core.management.base import BaseCommand

from pin.models_graph import FollowUser, UserGraph
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
                usr = follow_obj
                UserGraph.get_or_create("Person",
                                        usr.follower.username,
                                        usr.follower.profile.name,
                                        usr.follower.id)
                UserGraph.get_or_create("Person",
                                        usr.following.username,
                                        usr.following.profile.name,
                                        usr.following.id)

                FollowUser.get_or_create(start_id=usr.follower.id,
                                         end_id=usr.following.id,
                                         rel_type="follow")
            limit += 1001
            print limit
