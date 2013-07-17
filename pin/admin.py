# -*- coding: utf-8 -*-
from django.contrib import admin
#from django.contrib.comments.admin import CommentsAdmin
#from django.contrib.comments.models import Comment
from pin.models import Post, Notify, Category, App_data, Comments
from user_profile.models import Profile

import time

def make_approve(modeladmin, request, queryset):
    queryset.update(status=1, timestamp=time.time())
make_approve.short_description = u"تایید مظالب"

def make_approve_go_default(modeladmin, request, queryset):
    queryset.update(status=1,show_in_default=True, timestamp=time.time())
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

class CommentsAdmin(admin.ModelAdmin):
    list_display = ('comment', 'ip_address', 'user', 'object_pk', 'is_public', 'reported', 'admin_link')
    list_filter = ('is_public', 'reported')

    actions = ['accept', 'unaccept', 'delete_and_deactive_user', 'delete_all_user_comments']

    def accept(self, request, queryset):
        for obj in queryset:
            obj.is_public = True
            obj.save()
    accept.short_description = 'تایید'

    def unaccept(self, request, queryset):
        for obj in queryset:
            obj.is_public = False
            obj.save()
    unaccept.short_description = 'عدم تایید'

    def delete_and_deactive_user(self, request, queryset):
        for obj in queryset:
            user = obj.user
            user.is_active = False
            user.save()
            obj.delete()

    delete_and_deactive_user.short_description = 'حذف و غیر فعال کردن کاربر'

    def delete_all_user_comments(self, request, queryset):
        for obj in queryset:
            Comments.objects.filter(user=obj.user).delete()

    delete_all_user_comments.short_description = 'حذف تمام کامنت های این کاربر'

admin.site.register(Post, PinAdmin)
admin.site.register(Notify, NotifyAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(App_data, AppAdmin)
admin.site.register(Comments, CommentsAdmin)
