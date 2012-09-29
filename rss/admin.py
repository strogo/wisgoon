from django.contrib import admin
from rss.models import Feed, Item, Subscribe

class FeedAdmin(admin.ModelAdmin):
    list_display = ('url','title','last_fetch','followers','view','priority','creator','status')
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

admin.site.register(Feed,FeedAdmin)
admin.site.register(Item, FeedItemAdmin)
admin.site.register(Subscribe, SubscribeAdmin)