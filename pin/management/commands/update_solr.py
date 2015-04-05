from django.core.management.base import BaseCommand
from pin.models_redis import ChangedPosts
from pin.search_indexes import PostIndex
from pin.models import Post


class Command(BaseCommand):
    def handle(self, *args, **options):
        for i in range(1, 20):
            cp = ChangedPosts.get_changed()
            if not cp:
                continue
            print cp
            pi = PostIndex()
            pi.update_object(Post.objects.get(id=cp))
