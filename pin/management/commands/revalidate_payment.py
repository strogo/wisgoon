from django.core.management.base import BaseCommand

from pin.models import Bills2
from pin.tools import revalidate_bazaar


class Command(BaseCommand):
    def handle(self, *args, **options):
        for bill in Bills2.objects.filter(status=Bills2.VALIDATE_ERROR):
            print bill.id, bill.status, bill.trans_id
            print revalidate_bazaar(bill)
