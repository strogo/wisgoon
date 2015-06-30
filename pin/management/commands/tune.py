from django.core.management.base import BaseCommand

from pin.model_mongo import Notif


class Command(BaseCommand):
    def handle(self, *args, **options):
        print "tuning execute"
        notifs = Notif.objects.filter(seen=True)[:100]
        for n in notifs:
            n.delete()
