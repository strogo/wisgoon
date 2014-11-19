from django.core.management.base import BaseCommand
from django.conf import settings

from pin.models import Post

class Command(BaseCommand):
    def handle(self, *args, **options):
        print "approve posts"
        
        for p in Post.objects.filter(status=Post.PENDING)[:10]:
            p.approve()

        
