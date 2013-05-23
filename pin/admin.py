from django.contrib import admin

from pin.models import Post, Notify, Category

def make_approve(modeladmin, request, queryset):
    queryset.update(status=1)
make_approve.short_description = "Mark select as approved"

class PinAdmin(admin.ModelAdmin):
    list_filter = ('status',)
    list_display = ('id', 'text','user','category','admin_image','status',\
    'like', )
    actions=[make_approve]

class NotifyAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'user', 'text', 'seen', 'type')
    list_filter = ('seen',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id','title','admin_image')

admin.site.register(Post, PinAdmin)
admin.site.register(Notify, NotifyAdmin)
admin.site.register(Category, CategoryAdmin)
