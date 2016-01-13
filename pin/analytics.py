from datetime import datetime
from elasticsearch import Elasticsearch
es = Elasticsearch()

doc = {
    "parent_id":"t1_cqufim0",
   "controversiality":0,
   "distinguished":None,
   "body":"Are you really implying we return to those times ...",
   "retrieved_on":1432703079,
   "score":0,
   "author":"Wicked_Truth",
   "edited":False,
   "removal_reason":None,
   "gilded":0,
   "id":"cqug90i",
   "subreddit":"politics",
   "author_flair_text":None,
   "archived":False,
   "downs":0,
   "created_utc":"1430438400",
   "author_flair_css_class":None,
   "score_hidden":False,
   "name":"t1_cqug90i",
   "link_id":"t3_34f7mc",
   "ups":0,
   "subreddit_id":"t5_2cneq",
    'timestamp': datetime.now(),
}
res = es.index(index="test-index", doc_type='tweet', id=1, body=doc)
print(res['created'])

res = es.get(index="test-index", doc_type='tweet', id=1)
print(res['_source'])

es.indices.refresh(index="test-index")

res = es.search(index="test-index", body={"query": {"match_all": {}}})
print("Got %d Hits:" % res['hits']['total'])
for hit in res['hits']['hits']:
    print("%(timestamp)s %(author)s: %(text)s" % hit["_source"])
