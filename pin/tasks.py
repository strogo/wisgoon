import os
import redis
import json
import paramiko

from feedreader.celery import app
from django.conf import settings
from django.core.cache import cache

activityServer = redis.Redis(settings.REDIS_DB_3)


@app.task(name="wisgoon.pin.activity")
def activity(who, post_id, act_type):
    from pin.models import Follow
    flist = Follow.objects.filter(following_id=who)\
        .values_list('follower_id', flat=True)

    acts = activityServer.pipeline()
    for u in flist:
        key_prefix = "act:1.0:{}".format(u)
        # ActivityRedis(user_id=u).add_to_activity(act_type, who, post_id)
        data = "{}:{}:{}".format(act_type, who, post_id)
        acts.lpush(key_prefix, data)
        acts.ltrim(key_prefix, 0, 50)
    acts.execute()


@app.task(name="wisgoon.pin.add_to_storage")
def add_to_storage(post_id):
    from pin.models import Storages, Post
    post = Post.objects.get(id=post_id)
    storage = Storages.objects.order_by('num_files')[:1][0]

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(storage.host, username=storage.user)
    sftp = ssh.open_sftp()
    postmeta = post.postmetadata

    local_path = os.path.join(settings.MEDIA_ROOT, post.image)
    image_new_path = post.image
    image_new_path = image_new_path.replace(settings.INSTANCE_NAME, storage.name)
    remote_path = os.path.join(storage.path, image_new_path)
    remote_dir = os.path.dirname(remote_path)

    ssh.exec_command('mkdir -p ' + remote_dir)

    post.image = image_new_path
    post.save()
    sftp.put(local_path, remote_path)
    os.remove(local_path)

    local_path_236 = os.path.join(settings.MEDIA_ROOT, postmeta.img_236)
    image_new_path_236 = postmeta.img_236
    image_new_path_236 = image_new_path_236.replace(settings.INSTANCE_NAME, storage.name)
    remote_path_236 = os.path.join(storage.path, image_new_path_236)
    remote_dir = os.path.dirname(remote_path_236)

    postmeta.img_236 = image_new_path_236
    # postmeta.save()

    sftp.put(local_path_236, remote_path_236)
    os.remove(local_path_236)

    local_path_500 = os.path.join(settings.MEDIA_ROOT, postmeta.img_500)
    image_new_path_500 = postmeta.img_500
    image_new_path_500 = image_new_path_500.replace(settings.INSTANCE_NAME, storage.name)
    remote_path_500 = os.path.join(storage.path, image_new_path_500)
    remote_dir = os.path.dirname(remote_path_500)

    postmeta.img_500 = image_new_path_500
    postmeta.save()

    sftp.put(local_path_500, remote_path_500)
    os.remove(local_path_500)

    sftp.close()
    ssh.close()
    post.clear_cache()
    storage.num_files = storage.num_files + 3
    storage.save()

    check_porn.delay(post_id=post_id)

    return "add_to_storage"


@app.task(name="wisgoon.pin.check_porn")
def check_porn(post_id):
    from pin.models import Post
    import requests
    from requests.auth import HTTPBasicAuth
    import socket
    import paho.mqtt.publish as publish

    socket.setdefaulttimeout(10)

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return "post does not exists"
    # print post.get_image_500()
    img_url = post.get_image_500()['url']
    # print img_url
    r = requests.get(img_url)
    # print r
    # print r.content
    try:
        res = requests.post("https://188.75.73.226:1509/analyzer",
                            auth=HTTPBasicAuth('wisgoon94', 'Ghavi!394YUASTTH'),
                            verify=False, data=r.content)
        d = {
            "number": res.content,
            "image": post.get_image_236()['url'],
            "h": post.get_image_236()['h'],
            "id": post.id
        }
        if float(res.content) > 0.7:
            post.report = post.report + 10
            post.save()
        print d
        publish.single("wisgoon/check/porn", json.dumps(d), hostname="mosq.wisgoon.com", qos=2)
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

    local_path = os.path.join(settings.MEDIA_ROOT, str(profile.avatar))
    image_new_path = str(profile.avatar)
    image_new_path = image_new_path.replace(settings.INSTANCE_NAME, storage.name)
    remote_path = os.path.join(storage.path, image_new_path)
    remote_dir = os.path.dirname(remote_path)

    ssh.exec_command('mkdir -p ' + remote_dir)

    sftp.put(local_path, remote_path)
    os.remove(local_path)

    local_path = os.path.join(settings.MEDIA_ROOT, profile.get_avatar_64_str())
    image_new_path_64 = profile.get_avatar_64_str()
    image_new_path_64 = image_new_path_64.replace(settings.INSTANCE_NAME, storage.name)
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
    image_new_path = image_new_path.replace('avatars/%s' % settings.INSTANCE_NAME, "avatars/%s" % storage.name)
    remote_path = os.path.join(storage.path, image_new_path)
    remote_dir = os.path.dirname(remote_path)

    ssh.exec_command('mkdir -p ' + remote_dir)

    sftp.put(local_path, remote_path)
    # os.remove(local_path)

    local_path = os.path.join(settings.MEDIA_ROOT, profile.get_avatar_64_str())
    image_new_path_64 = profile.get_avatar_64_str()
    image_new_path_64 = image_new_path_64.replace('avatars/%s' % settings.INSTANCE_NAME, "avatars/%s" % storage.name)
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

            file_path = file_path.replace('./feedreader/media', storage.path)
            # file_path = file_path.replace('/feedreader/media/', storage.path)
            sftp.remove(file_path)
            sftp.close()
            ssh.close()
            exec_on_remote = True
            break

    if not exec_on_remote:
        os.remove(file_path)
    return "delete post", file_path


@app.task(name="wisgoon.pin.post_to_followers")
def post_to_followers(user_id, post_id):
    from pin.models import Follow
    followers = Follow.objects.filter(following_id=user_id)\
        .values_list('follower_id', flat=True)

    for follower_id in followers:
        post_to_follower_single.delay(post_id=post_id, follower_id=follower_id)
        # try:
        #     Post.add_to_user_stream(post_id=post_id, user_id=follower_id)
        # except Exception, e:
        #     print str(e)
        #     pass

    return "this is post_to_followers"


@app.task(name="wisgoon.pin.post_to_follower_single")
def post_to_follower_single(post_id, follower_id):
    from pin.models import Post
    Post.add_to_user_stream(post_id=post_id, user_id=follower_id)

    return "this is post_to_followers"
