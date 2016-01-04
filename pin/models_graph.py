# -*- coding:utf-8 -*-

from py2neo import Graph
from py2neo import Relationship
# from py2neo import neo4j
# from py2neo import rel
# from py2neo import Node

from django.conf import settings

try:
    graph = Graph(settings.NEO4J_DATABASE)
except Exception as e:
    print str(e), '1 models_graph'

try:
    indexes = graph.schema.get_indexes("Person")
    if 'user_id' not in indexes:
        graph.schema.create_index("Person", "user_id")
except Exception, e:
    print str(e), '2 models_graph'


class UserGraph():
    @classmethod
    def get_or_create(cls, lable, username, nickname, user_id):
        try:
            node = graph.merge_one(lable, "user_id", str(user_id))
            node['name'] = str(username)
            node['username'] = str(username)
            node.push()
            user_node = node
        except Exception as e:
            print str(e), '3 models_graph'
            user_node = False
        return user_node

    @classmethod
    def get_node(cls, lable, user_id):
        try:
            node = graph.find_one(lable,
                                  property_key="user_id",
                                  property_value=user_id)
        except Exception as e:
            print str(e), '4 models_graph'
            node = None
        return node

    @classmethod
    def delete_node(cls, node):
        try:
            graph.delete(node)
            status = True
        except Exception as e:
            print str(e), '5 models_graph'
            status = False
        return status


class FollowUser():

    @classmethod
    def get_relationship(cls, start_node, end_node, rel_type, bidirectional=False, limit=None):
        try:
            relation = list(graph.match(start_node=start_node,
                                        end_node=end_node,
                                        rel_type=rel_type,
                                        limit=limit,
                                        bidirectional=bidirectional))
        except Exception as e:
            print str(e), '6 models_graph'
            relation = None

        return relation

    @classmethod
    def get_or_create(cls, start_node, end_node, rel_type):
        try:
            relation = cls.get_relationship(start_node, end_node, rel_type)
            if not relation:
                relation = graph.create_unique(Relationship(start_node, rel_type, end_node))
        except Exception as e:
            print str(e), '7 models_graph'
            relation = None
        return relation

    @classmethod
    def delete_relations(cls, relations):
        try:
            for relation in relations:
                graph.delete(relation)
            status = True
        except Exception as e:
            print str(e), '8 models_graph'
            status = False
        return status


# class PostGraph():

#     @classmethod
#     def get_or_create(cls, post_obj):
#         post_id = int(post_obj.id)
#         category_id = int(post_obj.category_id)
#         try:
#             post_node = post.get_or_create("post_id", post_id, {
#                 "post_id": post_id,
#                 "category_id": category_id
#             })
#         except Exception as e:
#             print str(e)
#             post_node = False
#         return post_node

#     @classmethod
#     def from_to(cls, from_post, to_post):
#         if not from_post or not to_post:
#             return ''

#         rels = graph.match_one(
#             start_node=from_post,
#             end_node=to_post,
#             rel_type="FROM_TO")
#         if not rels:
#             graph.create(rel(from_post, "FROM_TO", to_post, **{"rate": 1}))
#         else:
#             p = rels.get_properties()
#             rate = p.get('rate', 1)
#             rels.update_properties({"rate": rate + 1})

#     @classmethod
#     def like(cls, user_id, post_id):
#         if not user_id or not post_id:
#             return ''

#         rels = graph.match_one(
#             start_node=user_id,
#             end_node=post_id,
#             rel_type="LIKED")
#         if not rels:
#             graph.create(rel(user_id, "LIKED", post_id))
#         # else:
#         #     #print rels, dir(rels)
#         #     p = rels.get_properties()
#         #     rate = p.get('rate', 1)
#         #     #print rate
#         #     rels.update_properties({"rate": rate + 1})

#     @classmethod
#     def suggest(cls, post_id):
#         try:
#             q = """
#             start n=node:post(post_id="%s")
#             match (n)-[r:GOTO]->(v)
#             return v, r order  by r.rate desc limit 3;""" % (post_id)

#             result = neo4j.CypherQuery(graph, q).execute()
#             vids = []
#             for c in result:
#                 vids.append(c['v']['post_id'])

#             return vids
#         except Exception, e:
#             print str(e)

"""
START p=node:Post(post_id = "3303226")
match (p)<-[:LIKED]-(u)-[r:LIKED]->(ap)
RETURN ap, count(r)
order by count(r) desc limit 100
"""
