from django.utils import timezone
from django.conf import settings
from pin.tasks import tick


def send_tick(doc):
    try:
        if settings.DEBUG:
            tick(doc=doc)
        else:
            tick.delay(doc=doc)
    except Exception, e:
        print str(e)


def like_act(post, actor):
    t_date = timezone.now()
    doc = {
        "@timestamp": str(t_date),
        "ip": "79.1.14.87",
        "type": "like",
        "actor": actor,
        "@message": "vahid like post {}".format(post),
    }

    send_tick(doc)
