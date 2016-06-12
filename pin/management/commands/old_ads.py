import redis

from django.core.management.base import BaseCommand
from django.conf import settings
from pin.models import Ad

r_server = redis.Redis(settings.REDIS_DB, db=settings.REDIS_DB_NUMBER)


class Command(BaseCommand):
    def handle(self, *args, **options):
        for ad in Ad.objects.filter(ended=False):
            key_name = "ad_{}".format(ad.id)
            r_server.delete(key_name)
