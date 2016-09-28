from influxdb import InfluxDBClient
# from django.utils import timezone
from django.conf import settings

# from pin.tasks import tick

try:
    client = InfluxDBClient(settings.INFLUX_HOST, 8086, timeout=1)
    client.create_database('wisgoonStats')
except Exception, e:
    pass


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
    json_body = [
        {
            "measurement": "actions",
            "tags": {
                "type": "comment",
            },
            "fields": {
                "value": 1
            }
        }
    ]

    send_tick(json_body)


def post_act(post, actor, category, user_ip="127.0.0.1"):
    json_body = [
        {
            "measurement": "actions",
            "tags": {
                "type": "post",
                "post_category": category,
            },
            "fields": {
                "value": 1
            }
        }
    ]

    send_tick(json_body)
