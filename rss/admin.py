from django.contrib import admin
from rss.models import Feed, Item, Subscribe, Search

def feed_unlock(modeladmin, request, queryset):
    queryset.update(lock=False)
feed_unlock.short_description = "unlock feeds"

class FeedAdmin(admin.ModelAdmin):
    list_display = ('url','title','last_fetch','followers','view','priority','creator','status','lock')
    fields = ('url',)
    actions = [feed_unlock]
    list_filter = ('lock',)
    
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

def tag_activate(modeladmin, request, queryset):
    queryset.update(accept=True)
tag_activate.short_description = "Mark selected tags published"

class SearchAdmin(admin.ModelAdmin):
    list_display = ('keyword', 'accept', 'count', 'slug')
    list_filter = ('accept',)
    fields = ('keyword', 'accept', 'count')
    actions = [tag_activate]

admin.site.register(Feed,FeedAdmin)
admin.site.register(Item, FeedItemAdmin)
admin.site.register(Subscribe, SubscribeAdmin)
admin.site.register(Search, SearchAdmin)
