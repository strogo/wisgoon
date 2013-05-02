from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from tastypie.http import HttpUnauthorized, HttpForbidden, HttpNotImplemented
from tastypie.resources import ModelResource
from tastypie.utils.urls import trailing_slash
from django.conf.urls import url

from tastypie.models import ApiKey
import hashlib
from pin.models import Post
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import Authorization

from daddy_avatar.templatetags import daddy_avatar

class UserResource(ModelResource):
    class Meta:
    #    queryset = User.objects.all()
    #    fields = ['first_name', 'last_name', 'email']
        allowed_methods = ['get', 'post']
        resource_name = 'user'

    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/login%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('login'), name="api_login"),
            url(r'^(?P<resource_name>%s)/logout%s$' %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('logout'), name='api_logout'),
            url(r'^(?P<resource_name>%s)/register%s$' %                           
                (self._meta.resource_name, trailing_slash()),                   
                 self.wrap_view('register'),name='api_register'),
        ]

    def register(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        data = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE','application/json'))
        
        app_token = hashlib.sha1('app mobile-)**Z{QT').hexdigest()
        req_token = data.get('token', '')

        if req_token != app_token:
            return self.create_response(request, {'success': False,'reason':
            'token problem for register'})
        

        username = data.get('username', '')
        email = data.get('email','')
        password = data.get('password', '')

        if not username or not email or not password:
            return self.create_response(request, {'status': False, 'reason':'error in parameters'})
        
        try:
            user = User.objects.create_user(username=username, email=email,
                password=password)
        except:
            return self.create_response(request, {'status': False, 'reason': 'error in user creation'})

        if user:
            return self.create_response(request, {'status':True, 'reason': 'user createdsuccessfully'})
        else:
            return self.create_response(request, {'status':False, 'reason': 'problem in create user'})


    def login(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        data = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))
        
        app_token = hashlib.sha1('app mobile-)**Z{QT').hexdigest()

        req_token = data.get('token', '')
        
        if req_token != app_token:
            print "%s, %s" %(req_token, app_token)
            return self.create_response(request, {
                    'success': False,
                    'reason': 'token problem',
                    }, HttpForbidden )
            
        
        username = data.get('username', '')
        password = data.get('password', '')

        user = authenticate(username=username, password=password)
        
        if user:
            if user.is_active:
                login(request, user)
                
                api_key, created = ApiKey.objects.get_or_create(user=user)
                
                return self.create_response(request, {
                    'success': True,
                    'token': api_key.key,
                    'id': user.id,
                    'user_avatar': daddy_avatar.daddy_avatar(user.email)                    
                })
            else:
                return self.create_response(request, {
                    'success': False,
                    'reason': 'disabled',
                    }, HttpForbidden )
        else:
            return self.create_response(request, {
                'success': False,
                'reason': 'incorrect',
                }, HttpUnauthorized )

    def logout(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        if request.user and request.user.is_authenticated():
            logout(request)
            return self.create_response(request, { 'success': True })
        else:
            return self.create_response(request, { 'success': False }, HttpUnauthorized)
