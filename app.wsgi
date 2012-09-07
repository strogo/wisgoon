import os, sys
os.environ['PYTHON_EGG_CACHE'] = '/opt/cache/.egg_cache'
sys.path.append('/usr/lib/python2.7/site-packages/django')
sys.path.append('/usr/lib/build/django/django')
sys.path.append('/var/www/html/')
sys.path.append('/var/www/html/feedreader')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "feedreader.settings")


import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
