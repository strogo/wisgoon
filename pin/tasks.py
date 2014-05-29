# -*- coding: utf-8 -*-
from __future__ import absolute_import

from datetime import datetime

#from pin.celery import app
from pin.models import Notifbar
from pin.model_mongo import Notif


#@app.task
def send_notif(user, type, post, actor, seen=False):
    """
    notif, created = Notif.objects.get_or_create(user=user, type=type, post_id=post)

    notif.seen = seen
    notif.date = datetime.now()
    notif.save()

    Notif_actors.objects.get_or_create(notif=notif, actor=actor)"""
    return True


def send_notif_bar(user, type, post, actor, seen=False):
    print "call me"
    #notif, created = Notifbar.objects.get_or_create(user=user, type=type, post_id=post, actor=actor)

    #Location.objects(user_id=user_id).update_one(set__point=point, upsert=True)
    Notif.objects(owner=user.id, type=type, post=post)\
        .update_one(set__last_actor=actor.id,
                    set__date=datetime.now,
                    set__seen=False,
                    add_to_set__actors=actor.id, upsert=True)

    return None
