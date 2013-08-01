from django.db.models import F
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from tastypie.models import ApiKey

from pin.models import Post, Likes, Comments

def check_auth(request):
    token = request.GET.get('token','')
    if not token:
        return False
    
    try:
        api = ApiKey.objects.get(key=token)
        user = api.user
        user._ip = request.META.get("REMOTE_ADDR", '127.0.0.1')

        return user
    except ApiKey.DoesNotExist:
        return False

    return False
    
@csrf_exempt
def like(request):
    user = check_auth(request)

    if not user:
        return HttpResponse('error in user validation')
        
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
            
            like.ip = user._ip
            like.save()
            
            return HttpResponse('+1')
        elif like:
            like.delete()

            Post.objects.filter(pk=post_id).update(like=F('like')-1)
            
            return HttpResponse('-1')

    return HttpResponse('error in parameters')

@csrf_exempt
def post_comment(request):
    user = check_auth(request)
    if not user:
        return HttpResponse('error in user validation')

    data = request.POST.copy()
    comment = data.get('comment')
    object_pk = data.get("object_pk")
    if data and comment and object_pk and Post.objects.filter(pk=object_pk).exists():

        Comments.objects.create(object_pk_id=object_pk, comment=comment, user=user, ip_address=user._ip)
        return HttpResponse(1)

    return HttpResponse(0)

@csrf_exempt
def post_report(request):
    user = check_auth(request)
    if not user:
        return HttpResponse('error in user validation')

    data = request.POST.copy()
    post_id = data['post_id']
    print post_id

    if data and post_id and Post.objects.filter(pk=post_id).exists():
        Post.objects.filter(pk=post_id).update(report=F('report')+1)
        return HttpResponse(1)

    return HttpResponse(0)


