from django.conf import settings
from johnny.cache import enable

if settings.DEBUG == False:
	enable()
	print "enable cache"
