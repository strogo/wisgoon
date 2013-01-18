#coding: utf-8
from django.shortcuts import render_to_response
from rss.sphinxapi import SPH_MATCH_ALL, SphinxClient, SPH_ATTR_TIMESTAMP,\
    SPH_MATCH_EXTENDED, SPH_SORT_TIME_SEGMENTS, SPH_SORT_ATTR_DESC

import datetime

def home(request):
    ## base of date range
    base = datetime.datetime.today()
    
    dateList=[]
    for x in range(0,14):
        ao = base - datetime.timedelta(days=x)
        ao = ao.strftime("%Y/%m/%d")
        dateList.append(ao)
        
    #print dateList
    dates,res, resCount  = [], [], []
    
    res.append(search_query('مشایی'))
    res.append(search_query('خامنه ای'))
    res.append(search_query('احمدی نژاد'))
    res.append(search_query('حداد عادل'))
    res.append(search_query('ولایتی'))
    
    for r in res:
        resCountList=[]
        #print "start resource"
        for dl in dateList:
            rsC = 0
            for od in r:
                if od in dl:
                    rsC=rsC+1
            resCountList.append(rsC)
            
        resCount.append(resCountList)

    #print date_data
    return render_to_response('elections/index.html',{'res': res, 'dateList':dateList, 'resCount':resCount})


def search_query(query, offset=0):
    
    mode = SPH_MATCH_EXTENDED
    host = 'localhost'
    port = 9312
    index = 'rss_item'
    filtercol = 'group_id'
    filtervals = []
    sortby = '-@date_added'
    groupby = 'id'
    groupsort = '@group desc'
    limit = 1000
    
    # do query
    cl = SphinxClient()
    cl.SetServer ( host, port )
    cl.SetWeights ( [100, 1] )
    cl.SetSortMode(SPH_SORT_ATTR_DESC, 'date_added')
    cl.SetMatchMode ( mode )

    #cl.SetSortMode(SPH_SORT_TIME_SEGMENTS)
    if limit:
        cl.SetLimits ( offset, limit, max(limit,1000) )
    res = cl.Query ( query, index )
    
    docs =[]
    for item in res['matches']:
        #print item['attrs']['date_abs']
        docs.append(item['attrs']['date_abs'])
    #print docs
    return docs
