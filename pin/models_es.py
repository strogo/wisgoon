from django.conf import settings
from elasticsearch import Elasticsearch

es = Elasticsearch(settings.ES_HOSTS)

es.indices.create(index='wisgoon-users', ignore=400)


class ESUsers():

    def fetch_user(self, user_id):
        pass

    def save(self, user_obj):
        doc = {
            'id': user_obj.id,
            'username': user_obj.username,
            'email': user_obj.email,
            'profile_name': user_obj.profile_object.name,
            'bio': user_obj.profile_object.bio,
            'cnt_followers': user_obj.profile_object.cnt_followers,
            'is_private': user_obj.profile_object.is_private,
        }
        es.index(index='wisgoon-users', doc_type='users',
                 id=user_obj.id, body=doc)
