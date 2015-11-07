import urllib2

base_url = "http://wisgoon.com/api/v6/post/item/%d/"

for i in range(6860, 10000000):
    try:
        r = urllib2.urlopen(base_url % i)
        print r.code
        print base_url % i
    except Exception, e:
        print str(e)
