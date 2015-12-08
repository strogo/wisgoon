import redis

from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.management import call_command

from mongoengine.connection import get_connection, disconnect


class Command(BaseCommand):
    def handle(self, *args, **options):
        clear_mongo(self)
        clear_redis(self)
        clear_mysql_data(self)


def clear_mongo(self):
    response = raw_input("Are You Sure Drop Collection? yes or no: ")
    if settings.DEBUG and response == 'yes':
        try:
            connection = get_connection()
            connection.drop_database('wisgoon')
            disconnect()

        except Exception as e:
            self.stdout.write(str(e))

        self.stdout.write('Dropping mongo test database: wisgoon')
    else:
        self.stdout.write("You're not in Debug Mode or wrongly is entered word")


def clear_redis(self):
    response = raw_input("Are You Sure clear all keys? yes or no: ")
    if settings.DEBUG and response == 'yes':
        try:
            r_server = redis.Redis(settings.REDIS_DB,
                                   db=settings.REDIS_DB_NUMBER)
            r_server.flushall()
        except Exception as e:
            self.stdout.write(str(e))

        self.stdout.write('Dropping All Keys in redis')
    else:
        self.stdout.write("You're not in Debug Mode or wrongly is entered word")


def clear_mysql_data(self):
    response = raw_input("Are You Sure clear all data? yes or no: ")
    if settings.DEBUG and response == 'yes':
        call_command('flush')
        self.stdout.write('Remove All data in mysql')
    else:
        self.stdout.write("You're not in Debug Mode or wrongly is entered word")
