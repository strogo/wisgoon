from django.core.management.base import BaseCommand
from pin.models_es import ESPosts
from pin.models import Post


class Command(BaseCommand):

    def handle(self, *args, **options):
        ps = ESPosts()
        limit = 100
        offset = 0
        last_post = Post.objects.only('id').last()

        while offset < last_post.id:
            posts = Post.objects.filter(id__range=(offset, offset + limit))
            for p in posts:
                ps.save(p)
            offset = offset + limit
