# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.comments.admin import CommentsAdmin
from django.contrib.comments.models import Comment
from pin.models import Post, Notify, Category, App_data
from user_profile.models import Profile

class PinCommentsAdmin(CommentsAdmin):
    list_display = ('name', 'content_type', 'object_pk', 'ip_address',
    'submit_date', 'is_public', 'is_removed','comment')

def make_approve(modeladmin, request, queryset):
    queryset.update(status=1)
make_approve.short_description = u"تایید مظالب"

def make_approve_go_default(modeladmin, request, queryset):
    queryset.update(status=1,show_in_default=True)
make_approve_go_default.short_description = u"تایید و ارسال برای صفحه اصلی"

class PinAdmin(admin.ModelAdmin):
    list_filter = ('status', 'is_ads','show_in_default', 'category')
    search_fields = ['id']
    list_display = ('id', 'text','user','category','admin_image','status',\
    'like', 'device', 'is_ads', 'show_in_default')
    actions=[make_approve, make_approve_go_default,'really_delete_selected']

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
    really_delete_selected.short_description = "حذف انتخاب شده ها"


class NotifyAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'text', 'seen', 'type')
    list_filter = ('seen',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id','title','admin_image')

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'cnt_post', 'cnt_like', 'score',
    'user', 'trusted')
    search_fields = ['user__id','name']
    list_filter = ('trusted',)

class AppAdmin(admin.ModelAdmin):
    list_display = ('name', 'file', 'version', 'current')

admin.site.register(Post, PinAdmin)
admin.site.register(Notify, NotifyAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(App_data, AppAdmin)
admin.site.unregister(Comment)
admin.site.register(Comment, PinCommentsAdmin)
