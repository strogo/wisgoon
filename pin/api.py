from tastypie.resources import ModelResource
from pin.models import Post

class PostResource(ModelResource):
    class Meta:
        queryset = Post.objects.all().order_by('-id')[:10]
        resource_name = 'post'
