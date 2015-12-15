from django.core.management.base import BaseCommand

from pin.models_graph import UserGraph
from django.contrib.auth.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        for user in User.objects.all()[:2]:
            UserGraph.get_or_create(user_id=user.id,
                                    username=user.username,
                                    nickname=user.profile.name)
