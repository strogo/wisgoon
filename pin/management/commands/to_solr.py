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

        u = None
        all_rows = []

        for u in User.objects.values('id', 'username').filter(id__gt=cur_id)[:100]:
            try:
                p = Profile.objects.values('name', 'score').get(user_id=u['id'])
                row = {
                    "id": u['id'],
                    "name_s": p['name'],
                    "username_s": u['username'],
                    "name_t": p['name'],
                    "username_t": u['username'],
                    "score_i": p['score'],
                }
                
            except Profile.DoesNotExist:
                row = {
                    "id": u['id'],
                    "username_s": u['username'],
                    "username_t": u['username'],
                    "score_i": 0,
                }

            all_rows.append(row)
            cache.set('cur_solr_user_id', u['id'], 86400)

        if u:
            print "hey u"
        else:
            cache.delete('cur_solr_user_id')
            print "none"
            
        solr.add(all_rows)

        
        

        
