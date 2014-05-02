# -*- coding: utf-8 -*-
from __future__ import absolute_import

from datetime import datetime

#from pin.celery import app
from pin.models import Notif, Notif_actors, Notifbar


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
    notif, created = Notifbar.objects.get_or_create(user=user, type=type, post_id=post, actor=actor)

    return notif
