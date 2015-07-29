from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        from cqlengine import columns
        from cqlengine.models import Model
        from cqlengine import connection
        from cqlengine.management import sync_table
        connection.setup(['127.0.0.1'], "wisgoon")

        class Users(Model):
            firstname = columns.Text()
            age = columns.Integer()
            city = columns.Text()
            email = columns.Text()
            lastname = columns.Text(primary_key=True)

            def __repr__(self):
                return '%s %d' % (self.firstname, self.age)

        sync_table(Users)
        Users.create(firstname='Bob', age=35, city='Austin',
                     email='bob@example.com', lastname='Jones')
        q = Users.get(lastname='Jones')

        print q
        # Bob 35
