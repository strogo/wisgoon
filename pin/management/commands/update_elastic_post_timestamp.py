from django.core.management.base import BaseCommand
from pin.models import Post
from django.conf import settings
from elasticsearch import Elasticsearch
from elasticsearch import exceptions


INDEX_POST = 'wis-posts'


es = Elasticsearch(settings.ES_HOSTS)


class Command(BaseCommand):

    def handle(self, *args, **options):

        limit = 100
        offset = 19000000
        last_post = Post.objects.only('id').last()

        while offset < last_post.id:
            posts = Post.objects.filter(id__range=(offset, offset + limit))
            for p in posts:
                timestamp = int(p.create.strftime("%s"))
                update_timestamp(p.id, timestamp)
            offset = offset + limit
            print offset


def update_timestamp(post_id, timestamp):
    try:
        es.update(id=post_id,
                  doc_type='post',
                  index=INDEX_POST,
                  body={"doc": {"timestamp": timestamp}},
                  retry_on_conflict=5)
    except exceptions.TransportError:
        print "error"
    except Exception as e:
        print str(e)
