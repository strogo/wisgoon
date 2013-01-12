from django.conf import settings

def c_url( request ):
    return { 'c_url': request.get_full_path() }

def node_url(request):
    return {'NODE_URL': settings.NODE_URL}