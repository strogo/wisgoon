from django.utils import timezone
from django.conf import settings
from pin.tasks import tick


def send_tick(doc):
    # pass
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
        "ip": user_ip,
        "cnt_like": 1,
        "actor": actor,
        "@message": "like post {}".format(post),
    }

    send_tick(doc)


def comment_act(post, actor, user_ip):
    t_date = timezone.now().isoformat()
    doc = {
        "@timestamp": t_date,
        "action_type": "comment",
        "ip": user_ip,
        "actor": actor,
        "cnt_comment": 1,
        "@message": "comment post {}".format(post),
    }

    send_tick(doc)


def post_act(post, actor, category, user_ip="127.0.0.1"):
    t_date = timezone.now().isoformat()
    doc = {
        "@timestamp": t_date,
        "action_type": "post",
        "post_category": category,
        "ip": user_ip,
        "actor": actor,
        "cnt_post": 1,
        "@message": "send post {}".format(post),
    }

    send_tick(doc)
