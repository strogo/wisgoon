from influxdb import InfluxDBClient

from django.utils import timezone
# from django.conf import settings

# from pin.tasks import tick


client = InfluxDBClient('79.127.125.104', 8086)

client.create_database('wisgoonStats')


def send_tick(doc):
    try:
        client.write_points(doc, database="wisgoonStats")
    except Exception, e:
        print str(e)


def like_act(post, actor, user_ip):
    json_body = [
        {
            "measurement": "actions",
            "tags": {
                "type": "like",
            },
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
