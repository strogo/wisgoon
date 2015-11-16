from django.core.management.base import BaseCommand
from django.conf import settings

from user_profile.models import Profile


class Command(BaseCommand):
    def handle(self, *args, **options):
        for p in Profile.objects.filter(avatar__contains="avatars/2"):
            print p.avatar
            print p.id
