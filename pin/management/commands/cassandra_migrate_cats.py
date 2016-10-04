from django.core.management.base import BaseCommand

from pin.models import Post, Category
from pin.models_casper import CatStreams


class Command(BaseCommand):
    def handle(self, *args, **options):
        for cat in Category.objects.all():
            posts = [int(p) for p in Post.latest(0, cat.id, 10000)]
            if not posts:
                continue

            for p in Post.objects.filter(id__in=posts):
                stream = CatStreams()
                stream.add_post(p.category_id,
                                p.id,
                                p.user_id,
                                p.timestamp)
