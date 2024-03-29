from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.conf.urls import url
from django.conf import settings

from tastypie.models import ApiKey
import hashlib

from tastypie.http import HttpUnauthorized, HttpForbidden
from tastypie.resources import ModelResource
from tastypie.utils.urls import trailing_slash

from daddy_avatar.templatetags import daddy_avatar

# User = get_user_model()


class UserResource(ModelResource):
    class Meta:
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
                self.wrap_view('register'), name='api_register'),
        ]

    def register(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        data = self.deserialize(request, request.body,
                                format=request.META.get('CONTENT_TYPE',
                                                        'application/json'))

        app_token = hashlib.sha1(settings.APP_TOKEN_STR).hexdigest()
        req_token = None

        if req_token != app_token:
            return self.create_response(request, {
                'success': False,
                'reason': 'token problem for register'
            })

        # username = data.get('username', '')
        username = None
        # email = data.get('email', '')
        email = None
        # password = data.get('password', '')
        password = None

        if not username or not email or not password:
            return self.create_response(request, {
                'status': False,
                'reason': 'error in parameters'
            })

        try:
            user = User.objects.create_user(username=username,
                                            email=email,
                                            password=password)
        except:
            return self.create_response(request, {
                'status': False,
                'reason': 'error in user creation'
            })

        if user:
            return self.create_response(request, {
                'status': True,
                'reason': 'user createdsuccessfully'
            })
        else:
            return self.create_response(request, {
                'status': False,
                'reason': 'problem in create user'
            })

    def login(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        data = self.deserialize(request,
                                request.body,
                                format=request.META.get('CONTENT_TYPE',
                                                        'application/json'))

        app_token = hashlib.sha1(settings.APP_TOKEN_STR).hexdigest()

        req_token = None

        if req_token != app_token:
            print "%s, %s" % (req_token, app_token)
            return self.create_response(request, {
                'success': False,
                'reason': 'token problem',
            }, HttpForbidden)

        username = None
        # username = data.get('username', '')
        password = None
        # password = data.get('password', '')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)

                api_key, created = ApiKey.objects.get_or_create(user=user)

                return self.create_response(request, {
                    'success': True,
                    'token': api_key.key,
                    'id': user.id,
                    'user_avatar': daddy_avatar.get_avatar(user)
                })
            else:
                return self.create_response(request, {
                    'success': False,
                    'reason': 'disabled',
                }, HttpForbidden)
        else:
            return self.create_response(request, {
                'success': False,
                'reason': 'incorrect',
            }, HttpUnauthorized)

    def logout(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        if request.user and request.user.is_authenticated():
            logout(request)
            return self.create_response(request, {'success': True})
        else:
            return self.create_response(request, {
                'success': False
            }, HttpUnauthorized)
