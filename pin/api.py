import os
from tastypie.resources import ModelResource
from tastypie.paginator import Paginator
from tastypie import fields
from tastypie.cache import SimpleCache

from PIL import Image
from django.conf import settings
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType

from sorl.thumbnail import get_thumbnail
from pin.models import Post, Likes, Category
from pin.templatetags.pin_tags import get_username
from daddy_avatar.templatetags import daddy_avatar

class CategotyResource(ModelResource):
    class Meta:
        queryset = Category.objects.all()
        resource_name="category"

class LikesResource(ModelResource):
    class Meta:
        #queryset = Likes.objects.all()
        resource_name = 'likes'

class CommentResource(ModelResource):
    class Meta:
        allowed_methods = ['get']
        post_type = ContentType.objects.get(app_label="pin", model="post")
        queryset = Comment.objects.filter(content_type=post_type)
        resource_name = "comments"
        paginator_class = Paginator
        filtering = {
            "object_pk": ('exact',),
        }
    
    def applicable_filters(self, request, applicable_filters):
        base_object_list = super(CommentResource, self).apply_filters(request, applicable_filters)
        post_id = request.GET.get('post_id', None)
        print post_id
        filters = {}                                                            
                                                                                
        if post_id:
            filters.update(dict(object_pk=post_id))
                                                                                
        return base_object_list.filter(**filters).distinct()

                                                                     
    def dispatch(self, request_type, request, **kwargs):                        
        return super(CommentResource, self).dispatch(request_type, request, **kwargs)

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
    
    class Meta:
        queryset = Post.objects.filter(status=1).order_by('-id')
        resource_name = 'post'
        allowed_methods = ['get']
        paginator_class = Paginator
        fields = ['id','image','like','text','url']
        cache = SimpleCache()

    def apply_filters(self, request, applicable_filters):
        base_object_list = super(PostResource, self).apply_filters(request, applicable_filters)
        
        user_id = request.GET.get('user_id', None)
        category_id = request.GET.get('category_id', None)
        filters = {}
        
        if user_id:
            filters.update(dict(user_id=user_id))
        
        if category_id:
            category_ids = category_id.replace(',', ' ').split(' ')
            filters.update(dict(category_id__in=category_ids))

        return base_object_list.filter(**filters).distinct()
    
    def dispatch(self, request_type, request, **kwargs):
        self.thumb_size = request.GET.get(self.thumb_query_name, self.thumb_default_size)        
        return super(PostResource, self).dispatch(request_type, request, **kwargs)
    
    def dehydrate(self, bundle):
        id = bundle.data['id']
        o_image = bundle.data['image']
        im = get_thumbnail(o_image, self.thumb_size, quality=self.thumb_quality)
        bundle.data['thumbnail'] = im
        bundle.data['hw'] = "%sx%s" % (im.height, im.width) 
        bundle.data['permalink'] = '/pin/%d/' % (int(id))

        user_email = bundle.data['user_avatar']
        bundle.data['user_avatar'] = daddy_avatar.daddy_avatar(user_email)
        
        likers = Likes.objects.filter(post_id=id).all()
        ar = []
        for lk in likers:
            ar.append([lk.user.id,lk.user.username, daddy_avatar.daddy_avatar(lk.user.email)])

        bundle.data['likers'] = ar
        bundle.data['user_name'] = get_username(bundle.data['user'])
        
        if self.get_resource_uri(bundle) == bundle.request.path:
            # this is detail
            #del(bundle.data['thumbnail'])
                   
            img_path = os.path.join(settings.MEDIA_ROOT, o_image)
            print img_path
            im = Image.open(img_path)
            w,h = im.size
            bundle.data['large_hw'] = "%sx%s" % ( h,w )
        
        return bundle
