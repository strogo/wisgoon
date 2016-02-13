# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf import settings

if settings.DEBUG:
    from feedreader.task_cel_local import notif_send, profile_after_like,\
        profile_after_dislike, clear_notif
else:
    from feedreader.task_cel import notif_send, profile_after_like,\
        profile_after_dislike, clear_notif

from pin.tasks import post_to_followers


def send_notif(user, type, post, actor, seen=False):
    return True


def send_notif_bar(user, type, post, actor, seen=False, post_image=None):
    try:
        if settings.USE_CELERY:
            notif_send.delay(user, type, post, actor, seen=False,
                             post_image=post_image)
        else:
            notif_send(user, type, post, actor, seen=False,
                       post_image=post_image)
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


def send_clear_notif(user_id):
    if settings.USE_CELERY:
        clear_notif.delay(user_id=user_id)
    else:
        clear_notif(user_id=user_id)


def send_post_to_followers(user_id, post_id):
    if settings.USE_CELERY_V3:
        post_to_followers.delay(user_id=user_id, post_id=post_id)
    else:
        post_to_followers(user_id=user_id, post_id=post_id)
