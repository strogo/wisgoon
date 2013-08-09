
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden

def is_admin(user):
	if user.is_superuser:
		return True

	return False

def deactive_user(request, user_id):
	if not is_admin(request.user):
		return HttpResponseForbidden('cant access')
	user = User.objects.filter(pk=user_id).update(is_active = False)
	return HttpResponseRedirect(reverse('pin-user', args=[user_id]))

def active_user(request, user_id):
	if not is_admin(request.user):
		return HttpResponseForbidden('cant access')

	user = User.objects.filter(pk=user_id).update(is_active = True)
	return HttpResponseRedirect(reverse('pin-user', args=[user_id]))