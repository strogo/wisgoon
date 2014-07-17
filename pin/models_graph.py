#-*- coding:utf-8 -*-
import time
import datetime

from py2neo import neo4j
from py2neo import node, rel

try:
    graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")
    post = graph_db.get_or_create_index(neo4j.Node, "Post")
    user = graph_db.get_or_create_index(neo4j.Node, "User")
    
except Exception as e:
    print str(e), '15 models_graph'

class PostGraph():

    @classmethod
    def get_or_create(self, post_id):
        try:
            post_node = post.get_or_create("post_id", post_id, {
                "post_id": post_id
            })
        except Exception as e:
            print str(e)
            post_node = False
        return post_node


class UserGraph():

    @classmethod
    def get_or_create(self, user_id):
        try:
            user_node = user.get_or_create("user_id", user_id, {
                "user_id": user_id
            })
        except Exception as e:
            print str(e)
            user_node = False
        return user_node
