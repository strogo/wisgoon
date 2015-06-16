import time
from django.core.management.base import BaseCommand

from pin.models import Follow
from django.contrib.auth.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        for i in range(1, 100):
            t = str(time.time())
            username = "user_" + t
            email = "user_" + t + "@gmail.com"
            password = "user_" + t

            user = User.objects.create_user(username=username,
                                            email=email,
                                            password=password)

            Follow.objects.get_or_create(follower=user,
                                         following_id=1)
