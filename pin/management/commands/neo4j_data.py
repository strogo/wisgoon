from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from pin.models_graph import FollowUser, UserGraph
from pin.models import Follow


class Command(BaseCommand):
    def handle(self, *args, **options):
        create_user()
        create_follow()


def create_user():
    users = User.objects.all()
    for user in users:
        UserGraph.get_or_create("Person", user.username,
                                user.profile.name, user.id)
        print "create %s" % str(user.username)


def create_follow():
    follows_obj = Follow.objects.all()
    for follow_obj in follows_obj:
        user = UserGraph.get_node("Person", follow_obj.follower_id)
        target = UserGraph.get_node("Person", follow_obj.following_id)
        a = FollowUser.get_or_create(start_node=user, end_node=target, rel_type="follow")
        print a
        print "create %s" % str(follow_obj.id)
