# -*- coding:utf-8 -*-

import os
import time
import datetime
from tastypie.resources import ModelResource
from tastypie.paginator import Paginator
from tastypie import fields
from tastypie.cache import SimpleCache, NoCache
from tastypie.models import ApiKey
from tastypie.authorization import Authorization
from tastypie.authentication import ApiKeyAuthentication

from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from django.core.cache import cache

from tastypie.models import create_api_key
from tastypie.exceptions import Unauthorized

from PIL import Image

from sorl.thumbnail import get_thumbnail
from pin.models import Post, Likes, Category, Notif, Comments,\
    Notif_actors, App_data, Stream
from user_profile.models import Profile
from pin.templatetags.pin_tags import get_username
from daddy_avatar.templatetags import daddy_avatar

from pin.tools import userdata_cache, AuthCache, CatCache

models.signals.post_save.connect(create_api_key, sender=User)

CACHE_AVATAR = 0
CACHE_USERNAME = 1


class PostPaginator(Paginator):
    def get_count(self):
        return 1000


class UserResource(ModelResource):

    class Meta:
        queryset = User.objects.all()
        excludes = ['password', 'email', 'is_superuser', 'is_staff',
                    'is_active']


class AppResource(ModelResource):
    class Meta:
        allowed_methods = ['get']
        queryset = App_data.objects.all()
        resource_name = "app"
        paginator_class = Paginator
        filtering = {
            "current": ('exact'),
        }


class ProfileObjectsOnlyAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        # This assumes a ``QuerySet`` from ``ModelResource``.
        #return object_list.filter(user=bundle.request.user)
        return object_list

    def read_detail(self, object_list, bundle):
        # Is the requested object owned by the user?
        #return bundle.obj.user == bundle.request.user
        return object_list

    def create_list(self, object_list, bundle):
        # Assuming their auto-aassigned to ``user``.
        return object_list

    def create_detail(self, object_list, bundle):
        return bundle.obj.user == bundle.request.user

    def update_list(self, object_list, bundle):
        allowed = []

        # Since they may not all be saved, iterate over them.
        for obj in object_list:
            if obj.user == bundle.request.user:
                allowed.append(obj)

        return allowed

    def update_detail(self, object_list, bundle):
        return bundle.obj.user == bundle.request.user

    def delete_list(self, object_list, bundle):
        # Sorry user, no deletes for you!
        raise Unauthorized("Sorry, no deletes.")
        #pass

    def delete_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes.")
        #pass


class ProfileResource(ModelResource):
    user = fields.IntegerField(attribute='user__id')
    user_name = fields.CharField(attribute='user__username')

    class Meta:
        allowed_methods = ['get']
        ordering = ['score']
        queryset = Profile.objects.all()
        resource_name = "profile"
        paginator_class = Paginator
        #cache = SimpleCache()
        #authentication = ApiKeyAuthentication()
        #authorization = ProfileObjectsOnlyAuthorization()
        filtering = {
            "user": ('exact'),
        }

    def dehydrate(self, bundle):
        user = bundle.data['user']
        bundle.data['user_avatar'] = AuthCache.avatar(user, size=300)[1:]
        return bundle


class CategotyResource(ModelResource):
    class Meta:
        queryset = Category.objects.all()
        resource_name = "category"
        cache = SimpleCache()

    def get_list(self, request, **kwargs):
        base_bundle = self.build_bundle(request=request)
        objects = self.obj_get_list(bundle=base_bundle, **self.remove_api_resource_names(kwargs))
        sorted_objects = self.apply_sorting(objects, options=request.GET)

        paginator = self._meta.paginator_class(request.GET, sorted_objects, resource_uri=self.get_resource_uri(), limit=self._meta.limit, max_limit=self._meta.max_limit, collection_name=self._meta.collection_name)
        to_be_serialized = paginator.page()

        # Dehydrate the bundles in preparation for serialization.
        bundles = []

        for obj in to_be_serialized[self._meta.collection_name]:
            bundle = self.build_bundle(obj=obj, request=request)
            bundles.append(self.full_dehydrate(bundle, for_list=True))

        to_be_serialized[self._meta.collection_name] = bundles
        to_be_serialized = self.alter_list_data_to_serialize(request, to_be_serialized)
        res = self.create_response(request, to_be_serialized)
        return res

    def get_detail(self, request, **kwargs):
        print "get details"
        """
        Returns a single serialized resource.

        Calls ``cached_obj_get/obj_get`` to provide the data, then handles that result
        set and serializes it.

        Should return a HttpResponse (200 OK).
        """
        basic_bundle = self.build_bundle(request=request)

        try:
            obj = self.cached_obj_get(bundle=basic_bundle, **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return http.HttpNotFound()
        except MultipleObjectsReturned:
            return http.HttpMultipleChoices("More than one resource is found at this URI.")

        bundle = self.build_bundle(obj=obj, request=request)
        bundle = self.full_dehydrate(bundle)
        bundle = self.alter_detail_data_to_serialize(request, bundle)
        return self.create_response(request, bundle)


class LikesResource(ModelResource):
    user_url = fields.IntegerField(attribute='user__id', null=True)
    post_id = fields.IntegerField(attribute='post_id', null=True)

    class Meta:
        queryset = Likes.objects.all()
        resource_name = 'likes'
        excludes = ['ip', 'id']
        filtering = {
            "post_id": ("exact",),
        }
        cache = SimpleCache(timeout=15)

    def dehydrate(self, bundle):
        user = bundle.data['user_url']
        bundle.data['user_avatar'] = AuthCache.avatar(user)[1:]
        bundle.data['user_name'] = AuthCache.get_username(user)

        return bundle

    def get_list(self, request, **kwargs):
        pk = int(request.GET.get('post_id'))
        offset = int(request.GET.get('offset', 0))

        hstr = "like_cache_%s%s" % (pk, offset)
        hcpstr = "like_max_%d" % pk
        cp = cache.get(hcpstr)
        if cp:
            if offset > cp:
                cache.set(hcpstr, offset, 3600)
        else:
            cache.set(hcpstr, offset, 3600)

        c = cache.get(hstr)
        if c:
            return c

        base_bundle = self.build_bundle(request=request)
        objects = self.obj_get_list(bundle=base_bundle, **self.remove_api_resource_names(kwargs))
        sorted_objects = self.apply_sorting(objects, options=request.GET)

        paginator = self._meta.paginator_class(request.GET, sorted_objects, resource_uri=self.get_resource_uri(), limit=self._meta.limit, max_limit=self._meta.max_limit, collection_name=self._meta.collection_name)
        to_be_serialized = paginator.page()

        # Dehydrate the bundles in preparation for serialization.
        bundles = []

        for obj in to_be_serialized[self._meta.collection_name]:
            bundle = self.build_bundle(obj=obj, request=request)
            bundles.append(self.full_dehydrate(bundle, for_list=True))

        to_be_serialized[self._meta.collection_name] = bundles
        to_be_serialized = self.alter_list_data_to_serialize(request, to_be_serialized)
        res = self.create_response(request, to_be_serialized)
        cache.set(hstr, res, 3600)
        return res


class CommentResource(ModelResource):
    user_url = fields.IntegerField(attribute='user_id', null=True)
    object_pk = fields.IntegerField(attribute='object_pk_id', null=True)

    class Meta:
        allowed_methods = ['get']
        queryset = Comments.objects.filter(is_public=True)
        resource_name = "comments"
        paginator_class = Paginator
        #fields = ['id', 'comment', 'object_pk', 'user_id', 'score', 'submit_date']
        excludes = ['ip_address', 'is_public', 'object_pk', 'reported']
        cache = SimpleCache(timeout=300)
        limit = 10
        filtering = {
            "object_pk": ('exact',),
        }

    def dehydrate(self, bundle):
        user = bundle.data['user_url']

        bundle.data['user_avatar'] = AuthCache.avatar(user)
        bundle.data['user_name'] = AuthCache.get_username(user)
        return bundle

    def get_list(self, request, **kwargs):
        pk = int(request.GET.get('object_pk'))
        offset = int(request.GET.get('offset', 0))

        hstr = "cmn_cache_%s%s" % (pk, offset)
        hcpstr = "cmnt_max_%d" % pk
        cp = cache.get(hcpstr)
        if cp:
            if offset > cp:
                cache.set(hcpstr, offset, 3600)
        else:
            cache.set(hcpstr, offset, 3600)

        c = cache.get(hstr)
        if c:
            print "get from cache", hstr, hcpstr
            return c

        base_bundle = self.build_bundle(request=request)
        objects = self.obj_get_list(bundle=base_bundle, **self.remove_api_resource_names(kwargs))
        sorted_objects = self.apply_sorting(objects, options=request.GET)

        paginator = self._meta.paginator_class(request.GET, sorted_objects, resource_uri=self.get_resource_uri(), limit=self._meta.limit, max_limit=self._meta.max_limit, collection_name=self._meta.collection_name)
        to_be_serialized = paginator.page()

        # Dehydrate the bundles in preparation for serialization.
        bundles = []

        for obj in to_be_serialized[self._meta.collection_name]:
            bundle = self.build_bundle(obj=obj, request=request)
            bundles.append(self.full_dehydrate(bundle, for_list=True))

        to_be_serialized[self._meta.collection_name] = bundles
        to_be_serialized = self.alter_list_data_to_serialize(request, to_be_serialized)
        res = self.create_response(request, to_be_serialized)
        cache.set(hstr, res, 3600)
        return res


class PostResource(ModelResource):
    thumb_default_size = "100x100"
    thumb_size = "100x100"
    thumb_crop = 'center'
    thumb_quality = 99
    thumb_query_name = 'thumb_size'
    #user_name = fields.CharField(attribute='user__username')
    #user_avatar = fields.CharField(attribute='user__email')
    user = fields.IntegerField(attribute='user_id')
    likers = fields.ListField()
    like = fields.IntegerField(attribute='cnt_like')
    #category = fields.ToOneField(CategotyResource, 'category', full=True)
    category = fields.IntegerField(attribute='category_id')

    like_with_user = fields.BooleanField(default=False)
    popular = None
    just_image = 0
    cur_user = None
    show_ads = True
    dispatch_exec = False

    class Meta:
        queryset = Post.objects.filter(status=1).order_by('-id')
        resource_name = 'post'
        allowed_methods = ['get']
        paginator_class = PostPaginator
        fields = ['id', 'image', 'like', 'text', 'url', 'cnt_comment']
        cache = SimpleCache()

    def apply_filters(self, request, applicable_filters):
        base_object_list = super(PostResource, self)\
            .apply_filters(request, applicable_filters)
        userid = request.GET.get('user_id', None)
        category_id = request.GET.get('category_id', None)
        before = request.GET.get('before', None)
        popular = request.GET.get('popular', None)
        filters = {}

        if userid:
            filters.update(dict(user_id=userid))
            self.show_ads = False

        if category_id:
            category_ids = category_id.replace(',', ' ').split(' ')
            filters.update(dict(category_id__in=category_ids))
            self.show_ads = True

        if before:
            filters.update(dict(id__lt=before))
            self.show_ads = True

        if popular:
            self.show_ads = False
            date_from = None
            dn = datetime.datetime.now()
            if popular == 'month':
                date_from = dn - datetime.timedelta(days=30)
            elif popular == 'lastday':
                date_from = dn - datetime.timedelta(days=1)
            elif popular == 'lastweek':
                date_from = dn - datetime.timedelta(days=7)
            elif popular == 'lasteigth':
                date_from = dn - datetime.timedelta(hours=8)

            if date_from:
                start_from = time.mktime(date_from.timetuple())
                filters.update(dict(timestamp__gt=start_from))

        print filters

        return base_object_list.filter(**filters)

    def apply_sorting(self, object_list, options=None):
        base_object_list = super(PostResource, self).apply_sorting(object_list)
        sorts = []
        sorts.append('-is_ads')

        if self.popular in ['month', 'lastday', 'lastweek', 'lasteigth']:
            sorts.append("-cnt_like")
        else:
            sorts.append('-id')
        sorts.append('-is_ads')

        return base_object_list.order_by(*sorts)

    def pre_dispatch(self, request, token_name):
        self.dispatch_exec = True
        token = request.GET.get(token_name, '')
        if token:
            self.cur_user = AuthCache.id_from_token(token=token)

        self.thumb_size = request.GET.get(self.thumb_query_name,
                                          self.thumb_default_size)
        self.just_image = request.GET.get('just_image', 0)
        self.popular = request.GET.get('popular', None)

    def dispatch(self, request_type, request, **kwargs):
        self.dispatch_exec = True
        self.pre_dispatch(request, 'token')

        return super(PostResource, self)\
            .dispatch(request_type, request, **kwargs)

    def dehydrate(self, bundle):
        if self.dispatch_exec is False:
            self.pre_dispatch(bundle.request, 'api_key')

        id = bundle.data['id']
        o_image = bundle.data['image']

        c_str = "s2%s_%s_%s" % (o_image,self.thumb_size,self.thumb_quality)
        img_cache = cache.get(c_str)
        if img_cache:
            imo = img_cache
            #print imo, "cache"
        else:
            try:
                im = get_thumbnail(o_image,
                                   self.thumb_size,
                                   quality=self.thumb_quality,
                                   upscale=False)
                imo = {
                    'thumbnail': im.url,
                    'hw': "%sx%s" % (im.height, im.width)
                }
                cache.set(c_str, imo, 8600)
            except:
                imo = ""
            #print imo

        if imo:
            bundle.data['thumbnail'] = imo['thumbnail'].replace('/media/', '')
            bundle.data['hw'] = imo['hw']

        if int(self.just_image) == 1:
            for key in ['user', 'url', 'like', 'like_with_user',
                        'cnt_comment', 'category', 'text',
                        'image', 'likers', 'resource_uri']:
                del(bundle.data[key])

            return bundle

        bundle.data['permalink'] = '/pin/%d/' % (int(id))
        user = bundle.data['user']
        av = AuthCache.avatar(user_id=user)
        bundle.data['user_avatar'] = AuthCache.avatar(user_id=user)[1:]
        bundle.data['user_name'] = AuthCache.get_username(user_id=user)

        cat_id = bundle.data['category']
        c_cache = cache.get("cat_c"+str(cat_id))
        if c_cache:
            bundle.data['category'] = c_cache
        else:
            cat = Category.objects.get(id=cat_id)
            # cat = CatCache.get_cat(bundle.data['category'])
            cat_o = {
                 'id': cat.id,
                 'image': "/media/" + str(cat.image),
                 'resource_uri': "/pin/apic/category/"+str(cat.id)+"/",
                 'title': cat.title,
                 }

            bundle.data['category'] = cat_o
            cache.set("cat_c"+str(cat_id), cat_o, 86400)
        #del(bundle.data['category'])


        #print self.cur_user
        if self.cur_user:
            # post likes users
            c_key = "post_like_%s" % (id)

            plu = cache.get(c_key)
            if plu:
                #print "get like_with_user from memcache", c_key
                if self.cur_user in plu:
                    bundle.data['like_with_user'] = True
            else:
                post_likers = Likes.objects.values_list('user_id', flat=True).filter(post_id=id)
                cache.set(c_key, post_likers, 60 * 60)

                if self.cur_user in post_likers:
                    bundle.data['like_with_user'] = True

        
        if bundle.data['like'] == -1:
            bundle.data['like'] = 0

        if bundle.data['cnt_comment'] == -1:
            bundle.data['cnt_comment'] = 0

        if self.get_resource_uri(bundle) == bundle.request.path:
            # this is detail
            img_path = os.path.join(settings.MEDIA_ROOT, o_image)
            im = Image.open(img_path)
            w, h = im.size
            bundle.data['large_hw'] = "%sx%s" % (h, w)

            bundle.data['likers'] = []
        return bundle

    def get_list(self, request, **kwargs):
        
        base_bundle = self.build_bundle(request=request)
        objects = self.obj_get_list(bundle=base_bundle, **self.remove_api_resource_names(kwargs))
        sorted_objects = self.apply_sorting(objects, options=request.GET)

        paginator = self._meta.paginator_class(request.GET, sorted_objects, resource_uri=self.get_resource_uri(), limit=self._meta.limit, max_limit=self._meta.max_limit, collection_name=self._meta.collection_name)
        to_be_serialized = paginator.page()
        
        # Dehydrate the bundles in preparation for serialization.
        bundles = []

        for obj in to_be_serialized[self._meta.collection_name]:
            bundle = self.build_bundle(obj=obj, request=request)
            bundles.append(self.full_dehydrate(bundle, for_list=True))

        to_be_serialized[self._meta.collection_name] = bundles
        to_be_serialized = self.alter_list_data_to_serialize(request, to_be_serialized)
        res = self.create_response(request, to_be_serialized)
        
        return res


class NotifAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        Notif.objects.filter(user=bundle.request.user, seen=False).update(seen=True)
        return object_list.filter(user=bundle.request.user)


class NotifyResource(ModelResource):
    actors = fields.ListField()
    image = fields.CharField(attribute='post__image')
    like = fields.IntegerField(attribute='post__cnt_like')
    cnt_comment = fields.IntegerField(attribute='post__cnt_comment')
    text = fields.CharField(attribute='post__text')
    url = fields.CharField(attribute='post__url')
    post_id = fields.IntegerField(attribute='post_id')
    user_id = fields.IntegerField(attribute='user_id')
    post_owner_id = fields.IntegerField(attribute='post__user_id')
    category = fields.ToOneField(CategotyResource, 'post__category', full=True)
    like_with_user = fields.BooleanField(default=False)
    cur_user = None
    post = fields.ToOneField(PostResource, 'post')

    class Meta:
        resource_name = 'notify'
        allowed_methods = ['get']
        authentication = ApiKeyAuthentication()
        authorization = NotifAuthorization()
        queryset = Notif.objects.all().order_by('-date')
        paginator_class = Paginator
        cache = SimpleCache(timeout=600)
        filtering = {
            #"user_id": ('exact',),
            "seen": ('exact',),
        }

    def apply_authorization_limits(self, request, object_list):
        #print "hello"

        return object_list.filter(user=request.user)

    def dispatch(self, request_type, request, **kwargs):
        token = request.GET.get('token', '')
        if token:
            self.cur_user = AuthCache.id_from_token(token)

        return super(NotifyResource, self)\
            .dispatch(request_type, request, **kwargs)

    def dehydrate(self, bundle):
        id = bundle.data['id']
        o_image = bundle.data['image']
        try:
            im = get_thumbnail(o_image, "300x300", quality=99, upscale=False)
        except:
            im = ""

        if im:
            bundle.data['thumbnail'] = im
            bundle.data['hw'] = "%sx%s" % (im.height, im.width)

        """
        if self.cur_user:
            if Likes.objects.filter(post_id=bundle.data['post_id'],
                                    user=self.cur_user).count():
                bundle.data['like_with_user'] = True
        """

        if self.cur_user:
            id = bundle.data['post_id']
            # post likes users
            c_key = "post_like_%s" % (id)

            plu = cache.get(c_key)
            if plu:
                #print "get like_with_user from memcache", c_key
                if self.cur_user in plu:
                    bundle.data['like_with_user'] = True
            else:
                post_likers = Likes.objects.values_list('user_id', flat=True).filter(post_id=id)
                cache.set(c_key, post_likers, 60 * 60 * 60)

                if self.cur_user in post_likers:
                    bundle.data['like_with_user'] = True

        post_owner_id = bundle.data['post_owner_id']

        bundle.data['post_owner_avatar'] = AuthCache.avatar(post_owner_id)
        bundle.data['post_owner_user_name'] = AuthCache.get_username(post_owner_id)

        actors = Notif_actors.objects.filter(notif=id).order_by('id')[:10]
        ar = []
        for lk in actors:
            ar.append(
                [
                    lk.actor_id,
                    AuthCache.get_username(lk.actor_id),
                    AuthCache.avatar(lk.actor_id, size=100)
                ]
            )

        bundle.data['actors'] = ar

        return bundle


class StreamAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        return object_list.filter(user=bundle.request.user)


class StreamResource(ModelResource):
    post = fields.ForeignKey(PostResource, 'post', full=True)

    class Meta:
        queryset = Stream.objects.all().order_by('-date')
        authentication = ApiKeyAuthentication()
        authorization = StreamAuthorization()
