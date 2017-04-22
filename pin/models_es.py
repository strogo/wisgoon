# -*- coding: utf-8 -*-

import re

from django.conf import settings

from elasticsearch import Elasticsearch
from elasticsearch import exceptions

from pin.preprocessing import normalize_tags


es = Elasticsearch(settings.ES_HOSTS)

INDEX_USER = 'wis-users'
INDEX_POST = 'wis-posts'

try:
    es.indices.create(index=INDEX_USER, ignore=[400, 111])
    es.indices.create(index=INDEX_POST, ignore=[400, 111])
except Exception, e:
    print str(e)


class UserSearchModel():

    def __init__(self, **entries):
        self.__dict__.update(entries)


class PostSearchModel():

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


class ESPosts():

    def __init__(self):
        pass

    def get_post(self, post_id):
        post = None
        try:
            post = es.get(index=INDEX_POST, id=post_id)
            post = PostSearchModel(**post['hits']['hits']["_source"])
        except Exception as e:
            print str(e)

        return post

    def search(self, q, from_=0):
        posts = []
        res = es.search(index=INDEX_POST, q=q,
                        from_=from_, sort='timestamp:desc')

        for hit in res['hits']['hits']:
            posts.append(PostSearchModel(**hit["_source"]))
        return posts

    def save(self, post_obj):
        doc = {
            'id': post_obj.id,
            'text': post_obj.text,
            'timestamp': post_obj.timestamp,
            'status': post_obj.status,
            'category': post_obj.category_id,
            'cnt_like': post_obj.cnt_like,
            'cnt_comment': post_obj.cnt_comment,
            'hash': post_obj.hash,
            'author': post_obj.user_id,
            'tags': self.prepare_tags(post_obj)
        }
        try:
            es.index(index=INDEX_POST, doc_type='post',
                     id=post_obj.id, body=doc)
        except Exception as e:
            print str(e)

    def add_post(self, post_id):
        from pin.models import Post

        try:
            post_obj = Post.objects.only("id", "text", "timestamp", "status",
                                         "category", "cnt_like", "cnt_comment",
                                         "hash", "user")\
                .get(id=post_id)
        except:
            post_obj = None

        if post_obj:
            doc = {
                'id': post_obj.id,
                'text': post_obj.text,
                'timestamp': post_obj.timestamp,
                'status': post_obj.status,
                'category': post_obj.category_id,
                'cnt_like': post_obj.cnt_like,
                'cnt_comment': post_obj.cnt_comment,
                'hash': post_obj.hash,
                'author': post_obj.user_id,
                'tags': self.prepare_tags(post_obj)
            }
            try:
                es.index(index=INDEX_POST, doc_type='post',
                         id=post_obj.id, body=doc)
            except Exception as e:
                print str(e)

    def prepare_tags(self, post_obj):
        tags_list = []

        if post_obj.status == 0:
            return tags_list

        hash_tags = re.compile(ur'(?i)(?<=\#)\w+', re.UNICODE)
        tags = hash_tags.findall(post_obj.text)

        for tag in tags:
            if tag not in tags_list:
                tags_list.append(normalize_tags(tag))
        return tags_list

    def delete(self, post_id):
        try:
            es.delete(index=INDEX_POST, doc_type='post', id=post_id)
        except Exception as e:
            print str(e)

    def inc_cnt_like(self, post_id):
        try:
            es.update(id=post_id,
                      doc_type='post',
                      index=INDEX_POST,
                      body={"script": "ctx._source.cnt_like+=1"},
                      retry_on_conflict=5)
        except exceptions.TransportError:
            self.add_post(post_id=post_id)
        except Exception as e:
            print str(e)

    def decr_cnt_like(self, post_id):
        try:
            es.update(id=post_id,
                      doc_type='post',
                      index=INDEX_POST,
                      body={"script": "ctx._source.cnt_like-=1"},
                      retry_on_conflict=5)
        except exceptions.TransportError:
            self.add_post(post_id=post_id)
        except Exception as e:
            print str(e)

    def inc_cnt_comment(self, post_id):
        try:
            es.update(id=post_id,
                      doc_type='post',
                      index=INDEX_POST,
                      body={"script": "ctx._source.cnt_comment+=1"},
                      retry_on_conflict=5)
        except exceptions.TransportError:
            self.add_post(post_id=post_id)
        except Exception as e:
            print str(e)

    def decr_cnt_comment(self, post_id):
        try:
            es.update(id=post_id,
                      doc_type='post',
                      index=INDEX_POST,
                      body={"script": "ctx._source.cnt_comment-=1"},
                      retry_on_conflict=5)
        except exceptions.TransportError:
            self.add_post(post_id=post_id)
        except Exception as e:
            print str(e)

    def related_post(self, text, offset=0, limit=20):
        posts = []
        try:
            res = es.search(index=INDEX_POST,
                            body={
                                "query": {
                                    "more_like_this": {
                                        "fields": ["text"],
                                        "like": text,
                                        "min_term_freq": 1,
                                        "max_query_terms": 12
                                        # "boost": 20
                                    }
                                }
                            },
                            from_=offset,
                            filter_path=['hits.hits._source'],
                            # sort='timestamp:desc',
                            size=limit)

            for hit in res['hits']['hits']:
                posts.append(PostSearchModel(**hit["_source"]))
        except Exception, e:
            print str(e)
        return posts

    def search_tags(self, text, offset=0, limit=20):
        posts = []
        try:
            q = {
                "query": {
                    "match": {"tags": text}
                }
            }
            res = es.search(index=INDEX_POST, body=q,
                            from_=offset,
                            sort='timestamp:desc',
                            size=limit)
            for hit in res['hits']['hits']:
                posts.append(PostSearchModel(**hit["_source"]))
        except Exception, e:
            print str(e)

        return posts, res["hits"]["total"]

    def search_campaign(self, text, range_date=None,
                        order="timestamp", offset=0, limit=20, sort="asc"):
        posts = []
        try:
            if range_date:
                q = {
                    "sort": [
                        {"timestamp": {"order": sort}},
                    ],
                    "query": {
                        "bool": {
                            "filter": [
                                {"terms": {"tags": text}},
                                {"range": {
                                    "timestamp": {
                                        "gte": range_date[0],
                                        "lte": range_date[1],
                                    }
                                }}
                            ]
                        }
                    }
                }
            else:
                q = {
                    "sort": [
                        {"timestamp": {"order": sort}},
                    ],
                    "query": {
                        "match": {"tags": text}
                    }
                }

            order = "{}:{}".format(order, "desc")
            res = es.search(index=INDEX_POST,
                            body=q,
                            from_=offset,
                            sort=order,
                            size=limit)
            for hit in res['hits']['hits']:
                posts.append(PostSearchModel(**hit["_source"]))
        except Exception, e:
            print str(e)

        return posts

    def count_tags(self, text):
        count = 0
        try:
            q = {
                "query": {
                    "bool": {
                        "filter": [
                            {"term": {"tags": text}}
                        ]
                    }
                }
            }
            res = es.count(index=INDEX_POST, body=q, filter_path=['count'])
            count = res['count']
        except Exception, e:
            print str(e)
        return count
