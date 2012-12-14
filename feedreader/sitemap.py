from django.contrib.sitemaps import Sitemap
from rss.models import Feed

class RssFeedSitemap(Sitemap):
    changefreq = "never"
    priority = 0.5
    
    def items(self):
        return Feed.objects.filter(status=1)

    def lastmod(self, obj):
        return obj.last_fetch

