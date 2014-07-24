from django.core.management.base import BaseCommand
from django.conf import settings

from pin.models import Post

class Command(BaseCommand):
    def handle(self, *args, **options):
        print "tuning execute"
        
        for p in Post.accepted.order_by('timestamp')[:1000]:
            Post.add_to_stream(p)

        
