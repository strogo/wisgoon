import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings


class Command(BaseCommand):

    def handle(self, *args, **options):
        users = []

        file_path = os.path.join(
            settings.BASE_DIR, 'pin/management/commands/users.txt')
        with open(file_path) as f:
            lines = f.readlines()

        for line in lines:
            users.append(line.strip())

        users = User.objects.filter(username__in=users)
        for user in users:
            user.is_active = True
            user.save()
            print "user {} is active".format(user.username)
