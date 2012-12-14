# coding: utf-8
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.utils.feedgenerator import Rss201rev2Feed
from rss.models import Item, Feed as rss_feed

class CorrectMimeTypeFeed(Rss201rev2Feed):
    mime_type = 'application/xml'

class LatestItemFeed(Feed):
    feed_type = CorrectMimeTypeFeed
    title = 'آخرین مطالب فیدخوان - ویسگون'
    link = "http://www.wisgoon.com/feedreader/"
    description = 'آخرین مطالب وارد شده در بخش فیدخوان وب سایت ویسگون'
    #creator = "http://www.wisgoon.com"
    
    def items(self):
        return Item.objects.order_by('-id')[:30]
    
    def item_title(self, item):
        return item.title
    
    def item_description(self, item):
        return item.description
    
    def item_link(self, item):
        return item.get_absolute_url()
    
    def item_pubdate(self, item):
        return item.date

class FeedsListFeed(Feed):
    feed_type = CorrectMimeTypeFeed
    title = 'فهرست فیدها - ویسگون'
    link = "http://www.wisgoon.com/feedreader/"
    description = 'لیست فیدهای فیدخوان'
    #creator = "http://www.wisgoon.com"
    
    def items(self):
        return rss_feed.objects.filter(status=1).all()
    
    def item_title(self, item):
        return item.title
    
    def item_description(self, item):
        return item.title
    
    def item_link(self, item):
        return item.get_absolute_url()
    
    def item_pubdate(self, item):
        return item.last_fetch
        
    