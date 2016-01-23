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


def like_act(post, actor, user_ip):
    t_date = timezone.now().isoformat()
    doc = {
        "@timestamp": t_date,
        "type": "like",
        "ip": user_ip,
        "actor": actor,
        "@message": "like post {}".format(post),
    }

    send_tick(doc)


def comment_act(post, actor, user_ip):
    t_date = timezone.now().isoformat()
    doc = {
        "@timestamp": t_date,
        "type": "comment",
        "ip": user_ip,
        "actor": actor,
        "@message": "comment post {}".format(post),
    }

    send_tick(doc)
