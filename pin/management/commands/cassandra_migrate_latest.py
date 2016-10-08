from django.core.management.base import BaseCommand

from pin.models import Post
from pin.models_casper import CatStreams


class Command(BaseCommand):
    def handle(self, *args, **options):
        posts = [int(p) for p in Post.latest(0, 0, 10000)]

        for p in Post.objects.filter(id__in=posts):
            stream = CatStreams()
            stream.add_to_latest(p.category_id, p.id, p.user_id)
