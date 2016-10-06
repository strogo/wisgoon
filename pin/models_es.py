from django.conf import settings
from elasticsearch import Elasticsearch

es = Elasticsearch(settings.ES_HOSTS)

INDEX_USER = 'wis-users'

es.indices.create(index=INDEX_USER, ignore=[400, 111])


class UserSearchModel():
    def __init__(self, **entries):
        self.__dict__.update(entries)


class ESUsers():

    def __init__(self):
        pass

    def fetch_user(self, user_id):
        pass

    def search(self, q, from_=0):
        users = []
        res = es.search(index=INDEX_USER, q=q, from_=from_)
        for hit in res['hits']['hits']:
            users.append(UserSearchModel(**hit["_source"]))

        return users

    def save(self, user_obj):
        doc = {
            'id': user_obj.id,
            'username': user_obj.username,
            'email': user_obj.email,
            'profile_name': user_obj.profile.name,
            'bio': user_obj.profile.bio,
        }
        es.index(index=INDEX_USER, doc_type='users',
                 id=user_obj.id, body=doc)
