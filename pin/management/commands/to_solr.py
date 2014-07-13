#from __future__ import print_function
import pysolr

from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.contrib.auth.models import User
from django.conf import settings

from user_profile.models import Profile


class Command(BaseCommand):
    def handle(self, *args, **options):
    	solr = pysolr.Solr('http://localhost:8983/solr/wisgoon_user', timeout=10)
        print "tuning execute"

        cur_id = cache.get('cur_solr_user_id', 0)
        print "cur id is", cur_id

        all_rows = []

        for u in User.objects.values('id', 'username').filter(id__gt=cur_id)[:1000]:
        	p = Profile.objects.get_or_create(user_id=u['id'])
        	row = {
        		"id": u['id'],
        		"name_s": p.name,
        		"username_s": u['username'],
        		"name_t": p.name,
        		"username_t": u['username'],
        	}
        	all_rows.append(row)
        	cache.set('cur_solr_user_id', u['id'], 86400)
        	
        solr.add(all_rows)

        
        

        
