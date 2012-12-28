from tastypie.resources import ModelResource
from pin.models import Post

class PostResource(ModelResource):
    class Meta:
        queryset = Post.objects.all()[:5]
        resource_name = 'post'
