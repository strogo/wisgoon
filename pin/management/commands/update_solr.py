from django.core.management.base import BaseCommand
from pin.models_redis import ChangedPosts
from pin.search_indexes import PostIndex
from pin.models import Post


class Command(BaseCommand):
    def handle(self, *args, **options):
        for cp in ChangedPosts.get_changed():
            if not cp:
                return
            pi = PostIndex()
            pi.update_object(Post.objects.get(id=cp))
