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

    print "salam"
    return "salam"


@app.task(name="wisgoon.pin.say_salam")
def say_salam():
    """sends an email when feedback form is filled successfully"""
    print "salam"
    return "salam"


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
    from pin.models import Follow, Post
    print "this is post_to_followers"
    followers = Follow.objects.filter(following_id=user_id)\
        .values_list('follower_id', flat=True)

    for follower_id in followers:
        try:
            Post.add_to_user_stream(post_id=post_id, user_id=follower_id)
        except Exception, e:
            print str(e)
            pass

    return "this is post_to_followers"
