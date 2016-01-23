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
        "action_type": "like",
        "type_number": 1,
        "ip": user_ip,
        "actor": actor,
        "@message": "like post {}".format(post),
    }

    send_tick(doc)


def comment_act(post, actor, user_ip):
    t_date = timezone.now().isoformat()
    doc = {
        "@timestamp": t_date,
        "action_type": "comment",
        "type_number": 2,
        "ip": user_ip,
        "actor": actor,
        "@message": "comment post {}".format(post),
    }

    send_tick(doc)


def post_act(post, actor, category, user_ip="127.0.0.1"):
    t_date = timezone.now().isoformat()
    doc = {
        "@timestamp": t_date,
        "action_type": "post",
        "type_number": 3,
        "post_category": category,
        "ip": user_ip,
        "actor": actor,
        "@message": "send post {}".format(post),
    }

    send_tick(doc)
