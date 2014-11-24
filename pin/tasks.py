# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf import settings

if settings.DEBUG:
    from feedreader.task_cel_local import notif_send, profile_after_like,\
        profile_after_dislike
else:
    from feedreader.task_cel import notif_send, profile_after_like,\
        profile_after_dislike


def send_notif(user, type, post, actor, seen=False):
    return True


def send_notif_bar(user, type, post, actor, seen=False):
    try:
        if settings.USE_CELERY:
            notif_send.delay(user, type, post, actor, seen=False)
        else:
            notif_send(user, type, post, actor, seen=False)
    except Exception, e:
        print str(e)
    return None


def send_profile_after_like(user_id):
    if settings.USE_CELERY:
        profile_after_like.delay(user_id=user_id)
    else:
        profile_after_like(user_id=user_id)


def send_profile_after_dislike(user_id):
    if settings.USE_CELERY:
        profile_after_dislike.delay(user_id=user_id)
    else:
        profile_after_dislike(user_id=user_id)
