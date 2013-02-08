# -*- coding: utf-8 -*- 

from sphinxapi import SPH_MATCH_ALL, SphinxClient, SPH_ATTR_TIMESTAMP,\
    SPH_MATCH_EXTENDED, SPH_SORT_TIME_SEGMENTS
def search_query(query, offset):
    mode = SPH_MATCH_EXTENDED
    host = 'localhost'
    port = 9312
    index = 'rss_item'
    filtercol = 'group_id'
    filtervals = []
    sortby = '-@weights'
    groupby = 'id'
    groupsort = '@group desc'
    limit = 30
    
    # do query
    cl = SphinxClient()
    cl.SetServer ( host, port )
    cl.SetWeights ( [100, 1] )
    cl.SetMatchMode ( mode )

    #cl.SetSortMode(SPH_SORT_TIME_SEGMENTS)
    if limit:
        cl.SetLimits ( offset, limit, max(limit,1000) )
    res = cl.Query ( query, index )
    
    docs =[]
    for item in res['matches']:
        docs.append(item['id'])
    
    return docs


q ='god'
    
if q != '':
    
        offset = 0
        docs=search_query(q, offset)
        print docs
