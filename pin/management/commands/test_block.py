import time
from django.core.management.base import BaseCommand

from pin.models import Block
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

            Block.block_user(user_id=user.id, blocked_id=1)
