import os
from tastypie.resources import ModelResource
from tastypie.paginator import Paginator
from tastypie import fields
from tastypie.cache import SimpleCache
from tastypie.models import ApiKey
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import Authorization

from django.contrib.auth.models import User
from django.db import models
from tastypie.models import create_api_key

from tastypie.exceptions import Unauthorized

from PIL import Image
from django.conf import settings
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType

from sorl.thumbnail import get_thumbnail
from pin.models import Post, Likes, Category, Notify, Comments
from user_profile.models import Profile
from pin.templatetags.pin_tags import get_username
from daddy_avatar.templatetags import daddy_avatar

models.signals.post_save.connect(create_api_key, sender=User)

class UserResource(ModelResource):

    class Meta:
        queryset = User.objects.all()
        excludes = ['password', 'email', 'is_superuser', 'is_staff', 'is_active']


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
    user = fields.IntegerField(attribute = 'user__id')
    user_name = fields.CharField(attribute = 'user__username')

    class Meta:
        allowed_methods = ['get']
        queryset = Profile.objects.all()
        resource_name="profile"
        #authentication = ApiKeyAuthentication()
        #authorization = ProfileObjectsOnlyAuthorization()
        filtering = {
            "user":('exact'),
        }

    def dehydrate(self, bundle):
        bundle.data['user_avatar'] = daddy_avatar.get_avatar(bundle.data['user'], size=300)
        return bundle

class CategotyResource(ModelResource):
    class Meta:
        queryset = Category.objects.all()
        resource_name="category"

class LikesResource(ModelResource):
    class Meta:
        #queryset = Likes.objects.all()
        resource_name = 'likes'

class NotifyResource(ModelResource):
    all_actor = fields.ListField()
    class Meta:
        resource_name = 'notify'
        allowed_methods = ['get']
        queryset = Notify.objects.all().order_by('-id')
        paginator_class = Paginator
        filtering = {
            "user_id": ('exact',),
            "seen": ('exact',),
        }

    def dehydrate(self, bundle):
        print bundle
        return bundle

class CommentResource(ModelResource):
    user = fields.IntegerField(attribute = 'user__id',  null=True)
    object_pk = fields.IntegerField(attribute = 'object_pk_id',  null=True)
    class Meta:
        allowed_methods = ['get']
        queryset = Comments.objects.filter(is_public=True)
        resource_name = "comments"
        paginator_class = Paginator
        filtering = {
            "object_pk": ('exact',),
        }

    def dehydrate(self, bundle):
        bundle.data['user_avatar'] = daddy_avatar.get_avatar(bundle.data['user'], size=100)

        return bundle
        
class PostResource(ModelResource):  
    thumb_default_size = "100x100"
    thumb_size = "100x100"
    thumb_crop = 'center'
    thumb_quality = 99
    thumb_query_name = 'thumb_size'
    user_name = fields.CharField(attribute = 'user__username')
    user_avatar = fields.CharField(attribute = 'user__email')
    user = fields.IntegerField(attribute = 'user__id')
    likers = fields.ListField()
    category = fields.ToOneField(CategotyResource , 'category',full=True)

    like_with_user = fields.BooleanField(default=False)

    cur_user = None

    class Meta:
        queryset = Post.objects.filter(status=1).order_by('-is_ads','-id')
        resource_name = 'post'
        allowed_methods = ['get']
        paginator_class = Paginator
        fields = ['id','image','like','text','url']
        cache = SimpleCache()

    def apply_filters(self, request, applicable_filters):
        base_object_list = super(PostResource, self).apply_filters(request, applicable_filters)
        
        userid = request.GET.get('user_id', None)
        category_id = request.GET.get('category_id', None)
        filters = {}
        
        if userid:
            filters.update(dict(user_id=userid))
        
        if category_id:
            category_ids = category_id.replace(',', ' ').split(' ')
            filters.update(dict(category_id__in=category_ids))
        
        if not userid and not category_id:
            filters.update(dict(show_in_default=True))

        return base_object_list.filter(**filters).distinct()
    
    def dispatch(self, request_type, request, **kwargs):
        token = request.GET.get('token', '')
        if token:
            try:
                api = ApiKey.objects.get(key=token)                                     
                self.cur_user = api.user
            except:
                pass

        self.thumb_size = request.GET.get(self.thumb_query_name, self.thumb_default_size)        
        return super(PostResource, self).dispatch(request_type, request, **kwargs)
    
    def dehydrate(self, bundle):
        id = bundle.data['id']
        post = Post.objects.get(pk=id)
        post.view += 1
        post.save()
        
        o_image = bundle.data['image']
        try:
            im = get_thumbnail(o_image, self.thumb_size, quality=self.thumb_quality, upscale=False)
        except:
            im = ""

        if im:
            bundle.data['thumbnail'] = im
            bundle.data['hw'] = "%sx%s" % (im.height, im.width) 

        bundle.data['permalink'] = '/pin/%d/' % (int(id))

        user_email = bundle.data['user_avatar']
        bundle.data['user_avatar'] = daddy_avatar.get_avatar(bundle.data['user'], size=100)

        if self.cur_user:
            if Likes.objects.filter(post_id=id, user=self.cur_user).count():
                bundle.data['like_with_user'] = True

        bundle.data['user_name'] = get_username(bundle.data['user'])
        
        if self.get_resource_uri(bundle) == bundle.request.path:
            # this is detail
            #del(bundle.data['thumbnail'])
                   
            img_path = os.path.join(settings.MEDIA_ROOT, o_image)
            print img_path
            im = Image.open(img_path)
            w,h = im.size
            bundle.data['large_hw'] = "%sx%s" % ( h,w )

            likers = Likes.objects.filter(post_id=id).all()
            ar = []
            for lk in likers:
                ar.append([lk.user.id,lk.user.username,\
                daddy_avatar.get_avatar(lk.user, size=100)])
            
            bundle.data['likers'] = ar
                
        
        return bundle
