from django.contrib import admin
from rss.models import Feed, Item, Subscribe, Search

class FeedAdmin(admin.ModelAdmin):
    list_display = ('url','title','last_fetch','followers','view','priority','creator','status','lock')
    fields = ('url',)
    
    def save_model(self, request, obj, form, change):
        obj.creator = request.user
        obj.save()
        
        subscribe = Subscribe()
        subscribe.user = request.user
        subscribe.feed = obj
        subscribe.save()
        

class FeedItemAdmin(admin.ModelAdmin):
    list_display = ('id','title','feed', 'date', 'goto')
    search_fields = ['id']
    date_hierarchy = 'date'
    list_filter = ('date','feed__title')

class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('user','feed')
    
class SearchAdmin(admin.ModelAdmin):
    list_display = ('keyword', 'accept', 'count', 'slug')
    fields = ('keyword', 'accept', 'count')

admin.site.register(Feed,FeedAdmin)
admin.site.register(Item, FeedItemAdmin)
admin.site.register(Subscribe, SubscribeAdmin)
admin.site.register(Search, SearchAdmin)