# -*- coding: utf-8 -*-
import os
import time
import json
import paramiko
import requests

from feedreader.celery import app
from django.conf import settings
from django.core.cache import cache
from django.core.management import call_command


def make_like_data(post, actor, timestamp):
    data = {
        "notification": {
            "text": u"تصویر شمارا پسندید",
            "actor": actor,
            "date": timestamp,
            "post": post,
            "type": settings.NOTIFICATION_TYPE_LIKE,
        }
    }

    return data


def make_comment_data(post, actor, timestamp, comment):
    data = {
        "notification": {
            "text": u"برای تصویر شما نظر داد",
            "actor": actor,
            "date": timestamp,
            "comment": comment[0:100].strip(),
            "post": post,
            "type": settings.NOTIFICATION_TYPE_COMMENT,
        }
    }

    return data


@app.task(name="wisgoon.gcm.send")
def send_push(data, google_token):
    data = {
        "to": google_token,
        "priority": "high",
        "data": data,
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'key=AIzaSyBb2hrHjni36s1UG70f3t22s9AZ7LZmrow'}

    res = requests.post(url='https://android.googleapis.com/gcm/send',
                        data=json.dumps(data),
                        headers=headers,
                        timeout=2)

    print data
    print res, res.content


def gcm_push(user_id, action_type, post_id, actor_id, timestamp, comment=None):
    from pin.models import PhoneData
    from pin.api6.tools import get_simple_user_object, post_item_json
    timestamp = int(timestamp)
    try:
        up = PhoneData.objects.get(user_id=user_id)

        if up.logged_out:
            return

        if up.app_version < settings.GCM_VERSION:
            return

        if not up.google_token or up.google_token == 'NONE':
            return
    except PhoneData.DoesNotExist:
        return

    if settings.NOTIFICATION_TYPE_LIKE == action_type:
        need_fiedls = ['id', 'user', 'permalink']
        actor = get_simple_user_object(actor_id)
        post = post_item_json(post_id=post_id, fields=need_fiedls)

        push_data = make_like_data(post, actor, timestamp)
        send_push.delay(push_data, up.google_token)

    elif settings.NOTIFICATION_TYPE_COMMENT == action_type:
        need_fiedls = ['id', 'user', 'permalink']
        actor = get_simple_user_object(actor_id)
        post = post_item_json(post_id=post_id, fields=need_fiedls)

        push_data = make_comment_data(post, actor, timestamp, comment)
        send_push.delay(push_data, up.google_token)


@app.task(name="wisgoon.analytics.tick")
def tick(doc):
    pass
    # client.write_points(doc)
    # es.index(index="wisgoon-analytics", doc_type='log', body=doc)


@app.task(name="wisgoon.pin.activity")
def activity(act_type, who, post_id):
    from models_redis import ActivityRedis
    ActivityRedis.push_to_activity(act_type, who, post_id)


@app.task(name="wisgoon.pin.add_to_storage")
def add_to_storage(post_id):
    from pin.models import Storages, Post
    try:
        post = Post.objects.get(id=post_id)
    except Exception as e:
        return
    if not Storages.objects.exists():
        return
    storage = Storages.objects.order_by('num_files')[:1][0]

    ins_name = settings.INSTANCE_NAME

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(storage.host, username=storage.user)
    except Exception, e:
        print str(e)
        time.sleep(10)
        add_to_storage(post_id)
        return

    sftp = ssh.open_sftp()
    postmeta = post.postmetadata

    local_path = os.path.join(settings.MEDIA_ROOT, post.image)
    image_new_path = post.image
    image_new_path = image_new_path.replace(ins_name, storage.name)
    remote_path = os.path.join(storage.path, image_new_path)
    remote_dir = os.path.dirname(remote_path)

    ssh.exec_command('mkdir -p ' + remote_dir)

    post.image = image_new_path
    post.save()
    sftp.put(local_path, remote_path)
    # os.remove(local_path)

    local_path_236 = os.path.join(settings.MEDIA_ROOT, postmeta.img_236)
    image_new_path_236 = postmeta.img_236
    image_new_path_236 = image_new_path_236.replace(ins_name, storage.name)
    remote_path_236 = os.path.join(storage.path, image_new_path_236)
    remote_dir = os.path.dirname(remote_path_236)

    postmeta.img_236 = image_new_path_236
    # postmeta.save()

    sftp.put(local_path_236, remote_path_236)
    # os.remove(local_path_236)

    local_path_500 = os.path.join(settings.MEDIA_ROOT, postmeta.img_500)
    image_new_path_500 = postmeta.img_500
    image_new_path_500 = image_new_path_500.replace(ins_name, storage.name)
    remote_path_500 = os.path.join(storage.path, image_new_path_500)
    remote_dir = os.path.dirname(remote_path_500)

    postmeta.img_500 = image_new_path_500
    postmeta.save()

    sftp.put(local_path_500, remote_path_500)
    # os.remove(local_path_500)

    sftp.close()
    ssh.close()
    post.clear_cache()
    storage.num_files = storage.num_files + 3
    storage.save()

    check_porn.delay(post_id=post_id)
    try:
        from pin.api6.cache_layer import PostCacheLayer
        PostCacheLayer(post_id=post_id).delete()
    except Exception, e:
        print str(e)

    return "add_to_storage"


def recheck_post(post_id):
    print "requeue post {}".format(post_id)
    check_porn.delay(post_id)


@app.task(name="wisgoon.pin.check_porn")
def check_porn(post_id):
    from pin.models import Post, ReportedPost
    from pin.api_tools import media_abs_url
    import requests
    from requests.auth import HTTPBasicAuth
    import socket

    socket.setdefaulttimeout(10)

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return "post does not exists"
    img_url = media_abs_url(post.get_image_500()['url'], check_photos=True)
    print img_url

    try:
        r = requests.get(img_url, timeout=5)
    except requests.ConnectionError, e:
        print str(e)
        return
    except requests.exceptions.Timeout, e:
        print str(e)
        return
    except Exception, e:
        print str(e)
        return

    try:
        hba = HTTPBasicAuth('wisgoon94', 'Ghavi!394YUASTTH')
        url = "https://188.75.73.226:1509/nuditydetection?id={}"\
            .format(post_id)
        res = requests.post(url,
                            auth=hba,
                            verify=False, data=r.content, timeout=10)
        if res.status_code != 200:
            print res.status_code
            recheck_post(post_id)
            return
    except requests.ConnectionError, e:
        recheck_post(post_id)
        print str(e)
        return
    except requests.exceptions.Timeout, e:
        recheck_post(post_id)
        print str(e)
        return

    jdata = json.loads(res.content)

    post_val = jdata[str(post_id)][0]["BlackProbability"]

    if float(post_val) > 0.7:
        ReportedPost.post_report(post_id=post.id, reporter_id=11253)
    print "complete check at {} with score {}".format(post_id, post_val)


@app.task(name="wisgoon.pin.porn_feedback")
def porn_feedback(post_image, status="neg"):
    """Check porn feedback."""
    import socket
    import requests
    from requests.auth import HTTPBasicAuth
    socket.setdefaulttimeout(10)

    img_url = post_image
    r = requests.get(img_url)

    rurl = "https://188.75.73.226:1509/feedback/{}".format(status)
    print rurl
    auth = HTTPBasicAuth('wisgoon94', 'Ghavi!394YUASTTH')

    try:
        res = requests.post(rurl, auth=auth, verify=False, data=r.content)

        print res.content
        print "callback"

    except Exception, e:
        print str(e)


@app.task(name="wisgoon.pin.add_avatar_to_storage")
def add_avatar_to_storage(profile_id):
    from pin.models import Storages
    from user_profile.models import Profile
    profile = Profile.objects.get(id=profile_id)
    storage = Storages.objects.order_by('num_files')[:1][0]

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(storage.host, username=storage.user)
    sftp = ssh.open_sftp()

    ins_name = settings.INSTANCE_NAME

    local_path = os.path.join(settings.MEDIA_ROOT, str(profile.avatar))
    image_new_path = str(profile.avatar)
    image_new_path = image_new_path.replace(ins_name, storage.name)
    remote_path = os.path.join(storage.path, image_new_path)
    remote_dir = os.path.dirname(remote_path)

    ssh.exec_command('mkdir -p ' + remote_dir)

    sftp.put(local_path, remote_path)
    os.remove(local_path)

    local_path = os.path.join(settings.MEDIA_ROOT, profile.get_avatar_64_str())
    image_new_path_64 = profile.get_avatar_64_str()
    image_new_path_64 = image_new_path_64.replace(ins_name, storage.name)
    remote_path = os.path.join(storage.path, image_new_path_64)
    remote_dir = os.path.dirname(remote_path)

    ssh.exec_command('mkdir -p ' + remote_dir)

    profile.avatar = image_new_path
    profile.version = Profile.AVATAT_MIGRATED
    profile.save()
    sftp.put(local_path, remote_path)

    os.remove(local_path)

    sftp.close()
    ssh.close()
    storage.num_files = storage.num_files + 3
    storage.save()

    ava_str = settings.AVATAR_CACHE_KEY.format(profile.user_id)
    cache.delete(ava_str)

    return "add_avatar_to_storage"


@app.task(name="wisgoon.pin.migrate_avatar_storage")
def migrate_avatar_storage(profile_id):
    from pin.models import Storages
    from user_profile.models import Profile
    profile = Profile.objects.get(id=profile_id)
    storage = Storages.objects.order_by('num_files')[:1][0]

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(storage.host, username=storage.user)
    sftp = ssh.open_sftp()

    local_path = os.path.join(settings.MEDIA_ROOT, str(profile.avatar))
    image_new_path = str(profile.avatar)
    image_new_path = image_new_path\
        .replace('avatars/%s' % settings.INSTANCE_NAME, "avatars/%s" % storage.name)
    remote_path = os.path.join(storage.path, image_new_path)
    remote_dir = os.path.dirname(remote_path)

    ssh.exec_command('mkdir -p ' + remote_dir)

    sftp.put(local_path, remote_path)
    # os.remove(local_path)

    local_path = os.path.join(settings.MEDIA_ROOT, profile.get_avatar_64_str())
    image_new_path_64 = profile.get_avatar_64_str()
    image_new_path_64 = image_new_path_64\
        .replace('avatars/%s' % settings.INSTANCE_NAME, "avatars/%s" % storage.name)
    remote_path = os.path.join(storage.path, image_new_path_64)
    remote_dir = os.path.dirname(remote_path)

    ssh.exec_command('mkdir -p ' + remote_dir)

    profile.avatar = image_new_path
    profile.version = Profile.AVATAT_MIGRATED
    profile.save()
    sftp.put(local_path, remote_path)

    # os.remove(local_path)

    sftp.close()
    ssh.close()
    storage.num_files = storage.num_files + 3
    storage.save()

    return "migrate_avatar_storage"


@app.task(name="wisgoon.pin.say_salam")
def say_salam():
    """sends an email when feedback form is filled successfully"""
    return "say salam"


@app.task(name="wisgoon.pin.delete_image")
def delete_image(file_path):
    from pin.models import Storages
    exec_on_remote = False
    for storage in Storages.objects.all():
        if storage.name in file_path:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(storage.host, username=storage.user)
            sftp = ssh.open_sftp()

            file_path = os.path.join(storage.path, file_path)

            # file_path = file_path.replace('./feedreader/media', storage.path)
            # file_path = file_path.replace('/feedreader/media/', storage.path)
            print file_path
            try:
                sftp.remove(file_path)
            except IOError, e:
                print str(e), file_path
            sftp.close()
            ssh.close()
            exec_on_remote = True
            break

    if not exec_on_remote:
        try:
            os.remove(file_path)
        except Exception as e:
            return string(e), file_path
    return "delete post", file_path


@app.task(name="wisgoon.pin.post_to_followers")
def post_to_followers(user_id, post_id):
    from pin.models import Follow, Post
    followers = Follow.objects.filter(following_id=user_id)\
        .values_list('follower_id', flat=True)

    Post.add_to_users_stream(post_id, followers, user_id)

    return "this is post_to_followers"


@app.task(name="wisgoon.pin.post_to_follower_single")
def post_to_follower_single(post_id, follower_id, post_owner):
    from pin.models import Post
    Post.add_to_user_stream(post_id=post_id, user_id=follower_id,
                            post_owner=post_owner)

    return "this is post_to_followers"


@app.task(name="tasks.remove_from_stream")
def remove_from_stream(user_id, owner_id):
    from pin.models import Post
    posts = Post.objects.filter(user_id=owner_id).values_list('id', flat=True)

    user_stream = Post.user_stream_latest(user_id)

    for post_id in user_stream:
        if post_id in posts:
            Post.remove_post_from_stream(user_id, post_id)

    return "remove posts from stream user {}".format(user_id)


@app.task(name="tasks.update_camp_post")
def update_camp_post(camp_id):
    call_command('update_campaign_post', camp_id=camp_id)


@app.task(name="tasks.camp_scores")
def camp_scores(camp_id):
    call_command('campaign_scores', camp_id=camp_id)


@app.task(name="wisgoon.pin.ltrim_user_stream")
def ltrim_user_stream(user_id):
    from pin.models_casper import UserStream
    print "start ltrim %s" % user_id
    us = UserStream()
    us.ltrim(user_id)
    print "end ltrim %s" % user_id
