from django.utils import timezone
from django.conf import settings
from pin.tasks import tick


def send_tick(doc):
    return
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

    json_body = [
        {
            "measurement": "actions",
            "tags": {
                "type": "like",
            },
            "time": t_date,
            "fields": {
                "value": 1
            }
        }
    ]

    send_tick(json_body)


def comment_act(post, actor, user_ip="127.0.0.1"):
    t_date = timezone.now().isoformat()
    json_body = [
        {
            "measurement": "actions",
            "tags": {
                "type": "comment",
            },
            "time": t_date,
            "fields": {
                "value": 1
            }
        }
    ]

    send_tick(json_body)


def post_act(post, actor, category, user_ip="127.0.0.1"):
    t_date = timezone.now().isoformat()
    json_body = [
        {
            "measurement": "actions",
            "tags": {
                "type": "post",
                "post_category": category,
            },
            "time": t_date,
            "fields": {
                "value": 1
            }
        }
    ]

    send_tick(json_body)
