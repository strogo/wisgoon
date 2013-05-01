from django.contrib import admin

from pin.models import Post, Notify, Category

class PinAdmin(admin.ModelAdmin):
    list_display = ('id', 'text','user','category','admin_image' )
    
class NotifyAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'user', 'text', 'seen', 'type')
    list_filter = ('seen',)

class CategoryAdmin(admin.ModelAdmin):
    pass

admin.site.register(Post, PinAdmin)
admin.site.register(Notify, NotifyAdmin)
admin.site.register(Category, CategoryAdmin)
