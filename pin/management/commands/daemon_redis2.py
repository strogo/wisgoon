import inspect
import os

from django.core.management.base import BaseCommand

from pin.models import PostMetaData
from pin.models_redis import LikesRedis


class Command(BaseCommand):
    def handle(self, *args, **options):

        path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        fname = os.path.join(path, "db.txt")
        with open(fname) as f:
            content = f.readlines()
            for p in content:
                print p
                post_id = int(p.replace("postLikersV1", ""))
                print post_id

                try:
                    LikesRedis(post_id=post_id)
                except Exception, e:
                    print str(e)
