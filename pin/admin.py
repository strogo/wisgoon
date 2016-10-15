# -*- coding: utf-8 -*-
import time

from django.contrib import admin
from haystack.admin import SearchModelAdmin

from user_profile.models import Profile, CreditLog

from pin.models import Post, Category, App_data, Comments, InstaAccount,\
    Official, SubCategory, Packages, Bills2 as Bill, Ad, Log, PhoneData,\
    BannedImei, CommentClassification, CommentClassificationTags,\
    Results, Storages, Lable, UserActivitiesSample, UserLable, UserActivities, Campaign, SystemState, CampaignWinners
from pin.actions import send_notif
from pin.tools import revalidate_bazaar
from django.core.management import call_command


class StoragesAdmin(admin.ModelAdmin):
    list_display = ('name', 'used', 'num_files', 'path', 'host', 'user',)


class ResultsAdmin(admin.ModelAdmin):
    list_display = ('id', 'label', 'text')


class CommentClassificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'tag')


class CommentClassificationTagsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class BannedImeiAdmin(admin.ModelAdmin):
    list_display = ('id', 'imei', 'create_time', 'user')
    raw_id_fields = ("user",)

    search_fields = ["=imei", ]


class PhoneDataAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'imei',
        'os',
        'phone_model',
        'phone_serial',
        'android_version',
        'app_version'
    )
    raw_id_fields = ("user",)
    search_fields = ["=imei", "=user__username"]


class CreditLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'prof_id', 'amount', 'mode', 'create_time')
    list_filter = ('mode',)

    search_fields = ['prof_id', ]

    # date_hierarchy = 'create_time'


class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'admin_image', 'admin_image_device')


class LogAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'owner', 'user_id', 'action', 'object_id',
                    'content_type', '_get_thumbnail', 'create_time',
                    'ip_address', 'text')

    list_filter = ('action', 'content_type')

    search_fields = ['=owner', '=user__username', '=object_id']

    raw_id_fields = ("user",)

    def _get_thumbnail(self, obj):
        if obj.post_image:
            return u'<a href="%s" target="_blank"><img style="max-height:100px;" src="%s" /></a>' % (obj.post_image, obj.post_image)
        return u''
    _get_thumbnail.allow_tags = True

    def user_id(self, instance):
        return instance.user_id


class AdAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'ended', 'get_cnt_view',
                    'ads_type', 'start', 'end', 'get_owner', 'ip_address')

    raw_id_fields = ("post", "user")
    list_filter = ("ads_type", "ended")
    search_fields = ['user__username', 'post__id']

    # date_hierarchy = 'start'

    actions = ['ended', ]

    def ended(self, request, queryset):
        for obj in queryset:
            obj.ended = True
            obj.save()

    def post_id(self, instance):
        return instance.post_id

    def user_id(self, instance):
        return instance.user_id

    def get_owner(self, instance):
        if instance.owner:
            return instance.owner

        instance.owner = instance.post.user
        instance.save()
        return instance.owner


class PackagesAdmin(admin.ModelAdmin):
    list_display = ('title', 'name', 'wis', 'price', 'icon',)


class BillAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'amount', 'trans_id', 'user',
                    'create_date', 'create_time')
    list_filter = ('status',)
    raw_id_fields = ("user",)

    search_fields = ['user__id', 'user__username', 'trans_id']

    date_hierarchy = 'create_date'

    actions = ['is_fake',
               'is_compeleted',
               'revalidate']

    def is_fake(self, request, queryset):
        for obj in queryset:
            obj.status = Bill.FAKERY
            obj.save()

    is_fake.short_description = "فیک هستند"

    def revalidate(self, request, queryset):
        for obj in queryset:
            revalidate_bazaar(obj)

    revalidate.short_description = "بررسی مجدد"

    def is_compeleted(self, request, queryset):
        for obj in queryset:
            obj.status = Bill.COMPLETED
            obj.save()

    is_compeleted.short_description = "درست هستند"


class OfficialAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'mode')
    raw_id_fields = ("user",)


class InstaAccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'cat', 'insta_id', 'lc')
    raw_id_fields = ("user", "cat")


class PinAdmin(admin.ModelAdmin):
    list_filter = ('status', 'report', 'is_ads', 'show_in_default',
                   'category__title')

    search_fields = ['=id', '=user__id', '=hash']

    raw_id_fields = ("user",)

    list_display = ('id', 'text', 'get_user_url', 'admin_image',
                    'status', 'like', 'device', 'is_ads',
                    'show_in_default', 'report', 'hash')

    actions = ['make_approve',
               'really_delete_selected',
               'delete_all_user_posts',
               'no_problem']

    def get_actions(self, request):
        actions = super(PinAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def make_approve(self, request, queryset):
        for obj in queryset:
            obj.approve()

    make_approve.short_description = u"تایید مطلب"

    def no_problem(self, request, queryset):
        for obj in queryset:
            obj.report = 0
            obj.status = Post.APPROVED
            obj.save()

    no_problem.short_description = "عکس مشکلی نداره"

    def really_delete_selected(self, request, queryset):
        for obj in queryset:
            obj.delete()

        if queryset.count() == 1:
            message_bit = "1 pin entry was"
        else:
            message_bit = "%s pin entries were" % queryset.count()
        self.message_user(request, "%s successfully deleted." % message_bit)

    really_delete_selected.short_description = "حذف انتخاب شده ها"

    def delete_all_user_posts(self, request, queryset):
        for obj in queryset:
            for o in Post.objects.only('id').filter(user_id=obj.user_id):
                o.delete()
            for o in Comments.objects.filter(user_id=obj.user_id):
                o.delete()

    delete_all_user_posts.short_description = 'حذف تمام پست های کاربر'


# class NotifyAdmin(admin.ModelAdmin):
#     list_display = ('id', 'user', 'text', 'seen', 'type')
#     list_filter = ('seen',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'admin_image', 'parent', 'native_hashcode')


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'website', 'cnt_post', 'cnt_like', 'score',
                    'user', 'trusted')
    search_fields = ['=user__id', '=user__username', '=name']
    list_filter = ('trusted',)

    raw_id_fields = ("user", "trusted_by")


class AppAdmin(admin.ModelAdmin):
    list_display = ('name', 'file', 'version', 'current')


class CommentsAdmin(admin.ModelAdmin):
    list_display = ('id', 'comment', 'ip_address', 'is_public',
                    'reported', 'admin_link')

    raw_id_fields = ("user",)

    list_filter = ('submit_date', 'is_public', 'reported')
    search_fields = ['comment', 'ip_address', 'user__id', 'user__username']
    date_hierarchy = 'submit_date'

    actions = ['accept', 'unaccept', 'delete_and_deactive_user',
               'delete_all_user_comments']

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
            user = obj.user
            user.is_active = False
            user.save()
            Comments.objects.filter(user=obj.user).delete()

    delete_all_user_comments.short_description = 'حذف تمام کامنت های این کاربر و غیر فعال کردن کاربر'


class SearchCommentAdmin(SearchModelAdmin):
    list_display = ('id', 'comment', 'ip_address', 'is_public',
                    'reported', 'admin_link')

    raw_id_fields = ("user", "object_pk")

    list_filter = ('submit_date', 'is_public', 'reported')
    search_fields = ['comment', 'ip_address', 'user__id', 'user__username']
    # date_hierarchy = 'submit_date'

    actions = ['accept', 'unaccept', 'delete_and_deactive_user',
               'delete_all_user_comments']

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
            user = obj.user
            user.is_active = False
            user.save()
            Comments.objects.filter(user=obj.user).delete()

    delete_all_user_comments.short_description = 'حذف تمام کامنت های این کاربر و غیر فعال کردن کاربر'


class CategoriesInline(admin.TabularInline):
    model = UserActivitiesSample.categories.through
    extra = 1


class LableAdmin(admin.ModelAdmin):
    list_display = ('id', 'text')


class UserActivitiesSampleAdmin(admin.ModelAdmin):
    inlines = [
        CategoriesInline,
    ]
    model = UserActivitiesSample
    list_display = ('id', 'lable')

    def label(self, obj):
        return obj.lable.text


class UserLableAdmin(admin.ModelAdmin):
    list_display = ('id', 'lable', 'user')

    def lable(self, obj):
        return obj.lable.text

    def user(self, obj):
        return obj.user.username


class UserActivitiesAdmin(admin.ModelAdmin):
    list_display = ('id', 'activities', 'user', 'create_at', 'update_at')

    def user(self, obj):
        return obj.user.username


class WinnersInline(admin.TabularInline):
    model = Campaign.winners.through
    raw_id_fields = ('user',)
    extra = 1


class CampaignAdmin(admin.ModelAdmin):
    inlines = [
        WinnersInline,
    ]
    model = Campaign
    search_fields = ['winners']
    raw_id_fields = ('owner',)
    list_display = ('id', 'description', 'primary_tag', 'tags', 'is_current',
                    'start_date', 'end_date', 'expired', 'title')


class SystemStateAdmin(admin.ModelAdmin):
    list_display = ('id', 'writable')


class CampaignWinnersAdmin(admin.ModelAdmin):
    list_display = ('id', 'campaign_id', 'winners')
    actions = ['winners_list']
    search_fields = ['campaign']
    raw_id_fields = ('campaign',)

    def campaign_id(self, obj):
        return obj.campaign.id

    def winners_list(self, request, queryset):
        for obj in queryset:
            call_command('update_campaign_post', camp_id=obj.campaign_id)
            call_command('campaign_scores', camp_id=obj.campaign_id)

    winners_list.short_description = 'محاسبه نفرات برتر'
    campaign_id.admin_order_field = 'campaign_id'


admin.site.register(SystemState, SystemStateAdmin)
admin.site.register(Comments, SearchCommentAdmin)
admin.site.register(Post, PinAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(App_data, AppAdmin)
# admin.site.register(Comments, CommentsAdmin)
admin.site.register(InstaAccount, InstaAccountAdmin)
admin.site.register(Official, OfficialAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(Packages, PackagesAdmin)
admin.site.register(Bill, BillAdmin)
admin.site.register(Ad, AdAdmin)
admin.site.register(Log, LogAdmin)
admin.site.register(CreditLog, CreditLogAdmin)
admin.site.register(PhoneData, PhoneDataAdmin)
admin.site.register(BannedImei, BannedImeiAdmin)
admin.site.register(CommentClassification, CommentClassificationAdmin)
admin.site.register(CommentClassificationTags, CommentClassificationTagsAdmin)
admin.site.register(Results, ResultsAdmin)
admin.site.register(Storages, StoragesAdmin)
admin.site.register(Lable, LableAdmin)
admin.site.register(UserActivitiesSample, UserActivitiesSampleAdmin)
admin.site.register(UserLable, UserLableAdmin)
admin.site.register(UserActivities, UserActivitiesAdmin)
admin.site.register(Campaign, CampaignAdmin)
admin.site.register(CampaignWinners, CampaignWinnersAdmin)
