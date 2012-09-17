import sys
import os


sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__),'../'))

from django.core.management import setup_environ 
import settings_local 
setup_environ(settings_local)

from banner import init as ban_init
from ban.models import Blog

blog = Blog.objects.filter(status=0).all()

if blog.exists():
    print "Exists"
else:
    ban_init()

