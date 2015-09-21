from feedreader.celery import app
from pin.models import Follow, Post


@app.task(name="wisgoon.pin.say_salam")
def say_salam():
    """sends an email when feedback form is filled successfully"""
    print "salam"
    return "salam"


@app.task(name="wisgoon.pin.post_to_followers")
def post_to_followers(user_id, post_id):
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
