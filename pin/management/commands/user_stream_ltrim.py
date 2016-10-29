from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from pin.models_casper import UserStream


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = User.objects.only('id').order_by('-id')
        us = UserStream()
        for user in users:
            us.ltrim(user.id)
            print "Ltrim user stream {}".format(user.id)
