from django.core.management.base import BaseCommand
from django.conf import settings

from user_profile.models import Profile


class Command(BaseCommand):
    def handle(self, *args, **options):
        for p in Profile.objects.filter(avatar__contains="avatars/2"):
            p.store_avatars(update_model=True)
            from pin.tasks import migrate_avatar_storage
            migrate_avatar_storage.delay(profile_id=p.id)
            print p.avatar
            print p.id
