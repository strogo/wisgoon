from sphinxapi import *

import pprint

sc = SphinxClient()
sc.SetServer('localhost',9312)
sc.SetGroupBy('date_added',SPH_GROUPBY_DAY)
sc.SetFilter('feed_id',[10])
sc.SetLimits(0,20)

pprint.pprint( sc.Query(''))
