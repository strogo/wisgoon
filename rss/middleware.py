import urlparse
from rss.models import Search
class SeoQuery():
    def process_request(self, request):
        try:
            referef = request.META['HTTP_REFERER']
            o = urlparse.urlparse(referef)
            o = urlparse.parse_qs(o.query)
            if o: 
                qq = o['q']
                for q in qq:
                    searchObj, created = Search.objects.get_or_create(keyword=q)
                    if not created:
                        searchObj.count=searchObj.count+1
                        searchObj.save()
                
        except:
            pass