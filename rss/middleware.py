import urlparse
from rss.models import Search
from django.http import HttpResponsePermanentRedirect

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

class RedirectMiddleware:

    def process_request(self, request):
        try:
            if request.META['PATH_INFO']:
                path_info = request.META['PATH_INFO']
                if path_info.startswith('/feedreader/'):
                    url = path_info.replace('/feedreader/','/')
                    return HttpResponsePermanentRedirect(url)
        except:
            pass

