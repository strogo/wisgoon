from tastypie.resources import ModelResource
from sorl.thumbnail import get_thumbnail
from pin.models import Post

class PostResource(ModelResource):
    class Meta:
        queryset = Post.objects.all().order_by('-id')[:10]
        resource_name = 'post'

    def dehydrate(self, bundle):
        o_image = bundle.data['image']
        im = get_thumbnail(o_image, '100x100', crop='center', quality=99)
        bundle.data['thumbnail'] = im
        return bundle
