import datetime
from django.core.management.base import BaseCommand


from pin.models import Post


class Command(BaseCommand):
    def handle(self, *args, **options):
        minute = datetime.datetime.now().minute
        if minute % 30 == 0:
            print "fix in home"
            Post.fix_in_home()
