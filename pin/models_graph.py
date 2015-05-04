#-*- coding:utf-8 -*-

from py2neo import neo4j
from py2neo import rel

try:
    graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")

    post = graph_db.get_or_create_index(neo4j.Node, "Post")
    user = graph_db.get_or_create_index(neo4j.Node, "WisUser")

except Exception as e:
    print str(e), '15 models_graph'


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


class PostGraph():

    @classmethod
    def get_or_create(self, post_obj):
        post_id = int(post_obj.id)
        category_id = int(post_obj.category_id)
        try:
            post_node = post.get_or_create("post_id", post_id, {
                "post_id": post_id,
                "category_id": category_id
            })
        except Exception as e:
            print str(e)
            post_node = False
        return post_node

    @classmethod
    def from_to(cls, from_post, to_post):
        if not from_post or not to_post:
            return ''

        rels = graph_db.match_one(
            start_node=from_post,
            end_node=to_post,
            rel_type="FROM_TO")
        if not rels:
            graph_db.create(rel(from_post, "FROM_TO", to_post, **{"rate": 1}))
        else:
            #print rels, dir(rels)
            p = rels.get_properties()
            rate = p.get('rate', 1)
            #print rate
            rels.update_properties({"rate": rate + 1})

    @classmethod
    def like(self, user_id, post_id):
        if not user_id or not post_id:
            return ''

        rels = graph_db.match_one(
            start_node=user_id,
            end_node=post_id,
            rel_type="LIKED")
        if not rels:
            graph_db.create(rel(user_id, "LIKED", post_id))
        # else:
        #     #print rels, dir(rels)
        #     p = rels.get_properties()
        #     rate = p.get('rate', 1)
        #     #print rate
        #     rels.update_properties({"rate": rate + 1})

    @classmethod
    def suggest(self, post_id):
        try:
            q = """
            start n=node:post(post_id="%s")
            match (n)-[r:GOTO]->(v)
            return v, r order  by r.rate desc limit 3;""" % (post_id)

            result = neo4j.CypherQuery(graph_db, q).execute()
            vids = []
            for c in result:
                vids.append(c['v']['post_id'])

            return vids
        except Exception, e:
            print str(e)

"""
START p=node:Post(post_id = "3303226")
match (p)<-[:LIKED]-(u)-[r:LIKED]->(ap)
RETURN ap, count(r)
order by count(r) desc limit 100
"""
