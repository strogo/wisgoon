from django.core.management.base import BaseCommand

from pin.models import Ad


class Command(BaseCommand):
    def handle(self, *args, **options):
        for i in range(0, 16000):
            Ad.get_ad(user_id=i)
