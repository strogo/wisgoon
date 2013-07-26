from django.db.models import F
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from tastypie.models import ApiKey

from pin.models import Post, Likes

def check_auth(request):
    token = request.GET.get('token','')
    if not token:
        return HttpResponse('error in user validation')
    
    try:
        api = ApiKey.objects.get(key=token)
        return api.user
    except ApiKey.DoesNotExist:
        return HttpResponse('error in user validation')
    
@csrf_exempt
def like(request):
    user = check_auth(request)
        
    if request.method == 'POST' and user.is_active:
        try:
            post_id = int(request.POST['post_id'])
        except ValueError:
            return HttpResponse('erro in post id')

        if not Post.objects.filter(pk=post_id,status=1).exists():
            return HttpResponse('post not found')

        #like, created = Likes.objects.get_or_create(user=user, post=post)
        try:
            like = Likes.objects.get(user=user, post_id=post_id)
            created = False
        except Likes.DoesNotExist:
            like = Likes.objects.create(user=user, post_id=post_id)
            created = True

        if created:
            Post.objects.filter(pk=post_id).update(like=F('like')+1)
            
            like.ip = request.META.get("REMOTE_ADDR", '127.0.0.1')
            like.save()
            
            return HttpResponse('+1')
        elif like:
            like.delete()

            Post.objects.filter(pk=post_id).update(like=F('like')-1)
            
            return HttpResponse('-1')

    return HttpResponse('error in parameters')