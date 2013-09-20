from django.core.management.base import BaseCommand
from django.conf import settings

from rss.models import Feed
from feedreader.parser import parse_feed

class Command(BaseCommand):
    help = 'parse feed by priority'
    def handle(self, *args, **options):
        priority = int(args[0])
        limit=priority*3
        print "limit is ",limit
        feedObj = Feed.objects.filter(lock=False,priority=priority).all().order_by('last_fetch')[:limit]

        for i in feedObj:
            parse_feed(i)
        print priority
