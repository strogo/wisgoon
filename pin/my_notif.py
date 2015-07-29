from cqlengine import columns
from cqlengine.models import Model
from cqlengine import connection
from cqlengine.management import sync_table

try:
    connection.setup(['79.127.125.104'], "wisgoon")
except Exception, e:
    print "my notif line 10", str(e)


class NotifCas(Model):
    last_actor = columns.Integer()

    date = columns.DateTime()
    post = columns.Integer(primary_key=True)
    post_image = columns.Text()
    owner = columns.Integer(primary_key=True)
    actors = columns.List(columns.Integer)
    type = columns.Integer(primary_key=True)
    seen = columns.Boolean(default=False)

    # firstname = columns.Text()
    # age = columns.Integer()
    # city = columns.Text()
    # email = columns.Text()
    # lastname = columns.Text(primary_key=True)

    def __repr__(self):
        return '%s %d' % (self.firstname, self.age)

# drop_table(NotifCas)
try:
    sync_table(NotifCas)
except Exception, e:
    print "my notif line 36", str(e)
