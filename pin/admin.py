from django.contrib import admin

from pin.models import Post, Notify, Category

def make_approve(modeladmin, request, queryset):
    queryset.update(status=1)
make_approve.short_description = "Mark select as approved"

class PinAdmin(admin.ModelAdmin):
    list_filter = ('status','category', 'is_ads')
    search_fields = ['id']
    list_display = ('id', 'text','user','category','admin_image','status',\
    'like', 'device', 'url', 'is_ads')
    actions=[make_approve,'really_delete_selected']

    def get_actions(self, request):
        actions = super(PinAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def really_delete_selected(self, request, queryset):
        for obj in queryset:
            obj.delete()

        if queryset.count() == 1:
            message_bit = "1 pin entry was"
        else:
            message_bit = "%s pin entries were" % queryset.count()
        self.message_user(request, "%s successfully deleted." % message_bit)
    really_delete_selected.short_description = "Delete selected entries"


class NotifyAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'user', 'text', 'seen', 'type')
    list_filter = ('seen',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id','title','admin_image')

admin.site.register(Post, PinAdmin)
admin.site.register(Notify, NotifyAdmin)
admin.site.register(Category, CategoryAdmin)
