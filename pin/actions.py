# -*- coding: utf-8 -*-
from __future__ import absolute_import
# import time

from django.conf import settings

from pin.api6.tools import is_system_writable

from pin.tasks import post_to_followers

if settings.DEBUG:
    from feedreader.task_cel_local import notif_send, profile_after_like,\
        profile_after_dislike, clear_notif
else:
    from feedreader.task_cel import notif_send, profile_after_like,\
        profile_after_dislike, clear_notif


def send_notif(user, type, post, actor, seen=False):
    return True


def send_notif_bar(user, type, post, actor,
                   seen=False, post_image=None,
                   comment=None):
    if is_system_writable():
        try:
            if settings.USE_CELERY:
                # gcm_push(user, type, post, actor, time.time(), comment)
                notif_send.delay(user_id=user,
                                 type=type,
                                 post=post,
                                 actor_id=actor,
                                 seen=False,
                                 post_image=post_image,
                                 comment=comment)
            else:
                # gcm_push(user, type, post, actor, time.time(), comment)
                notif_send(user_id=user,
                           type=type,
                           post=post,
                           actor_id=actor,
                           seen=False,
                           post_image=post_image,
                           comment=comment)
        except Exception, e:
            print str(e)
    return None


def send_profile_after_like(user_id):
    if is_system_writable():
        if settings.USE_CELERY:
            profile_after_like.delay(user_id=user_id)
        else:
            profile_after_like(user_id=user_id)


def send_profile_after_dislike(user_id):
    if is_system_writable():
        if settings.USE_CELERY:
            profile_after_dislike.delay(user_id=user_id)
        else:
            profile_after_dislike(user_id=user_id)


def send_clear_notif(user_id):
    if is_system_writable():
        if settings.USE_CELERY:
            clear_notif.delay(user_id=user_id)
        else:
            clear_notif(user_id=user_id)


def send_post_to_followers(user_id, post_id):
    if settings.USE_CELERY:
        post_to_followers.delay(user_id=user_id, post_id=post_id)
    else:
        post_to_followers(user_id=user_id, post_id=post_id)
