import os
import paramiko

from feedreader.celery import app
from django.conf import settings


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
    image_new_path = image_new_path.replace('blackhole', storage.name)
    remote_path = os.path.join(storage.path, image_new_path)
    remote_dir = os.path.dirname(remote_path)

    ssh.exec_command('mkdir -p ' + remote_dir)

    post.image = image_new_path
    post.save()
    sftp.put(local_path, remote_path)
    os.remove(local_path)

    local_path_236 = os.path.join(settings.MEDIA_ROOT, postmeta.img_236)
    image_new_path_236 = postmeta.img_236
    image_new_path_236 = image_new_path_236.replace('blackhole', storage.name)
    remote_path_236 = os.path.join(storage.path, image_new_path_236)
    remote_dir = os.path.dirname(remote_path_236)

    postmeta.img_236 = image_new_path_236
    # postmeta.save()

    sftp.put(local_path_236, remote_path_236)
    os.remove(local_path_236)

    local_path_500 = os.path.join(settings.MEDIA_ROOT, postmeta.img_500)
    image_new_path_500 = postmeta.img_500
    image_new_path_500 = image_new_path_500.replace('blackhole', storage.name)
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

    return "add_to_storage"


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
    image_new_path = image_new_path.replace('blackhole', storage.name)
    remote_path = os.path.join(storage.path, image_new_path)
    remote_dir = os.path.dirname(remote_path)

    ssh.exec_command('mkdir -p ' + remote_dir)

    sftp.put(local_path, remote_path)
    os.remove(local_path)

    local_path = os.path.join(settings.MEDIA_ROOT, profile.get_avatar_64_str())
    image_new_path_64 = profile.get_avatar_64_str()
    image_new_path_64 = image_new_path_64.replace('blackhole', storage.name)
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
    image_new_path = image_new_path.replace('avatars', "avatars/%s" % storage.name)
    remote_path = os.path.join(storage.path, image_new_path)
    remote_dir = os.path.dirname(remote_path)

    ssh.exec_command('mkdir -p ' + remote_dir)

    sftp.put(local_path, remote_path)
    # os.remove(local_path)

    local_path = os.path.join(settings.MEDIA_ROOT, profile.get_avatar_64_str())
    image_new_path_64 = profile.get_avatar_64_str()
    image_new_path_64 = image_new_path_64.replace('avatars', "avatars/%s" % storage.name)
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
