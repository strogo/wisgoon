# coding: utf-8
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.utils.feedgenerator import Rss201rev2Feed

from pin.models import Post


class CorrectMimeTypeFeed(Rss201rev2Feed):
    mime_type = 'application/xml'


class EditorPinFeed(Feed):
    feed_type = CorrectMimeTypeFeed
    title = 'آخرین مطالب پین - ویسگون'
    link = "http://www.wisgoon.com/pin/"
    description = 'آخرین مطالب وارد شده در بخش پین وب سایت ویسگون'

    def items(self):
        return Post.objects.filter(show_in_default=True).order_by('-id')[:100]

    def item_title(self, item):
        return item.text[:80]

    def item_description(self, item):
        text = item.text
        img = item.get_image_500()
        if img:
            text = "<p>%s</p> <br><br> <img src='%s'>" % (text, img['url'])

        return text

    def item_link(self, item):
        return reverse('pin-item', args=[item.pk])

    def item_pubdate(self, item):
        return item.create
