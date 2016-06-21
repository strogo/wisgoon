
from stream_framework.activity import Activity
from stream_framework.verbs.base import Verb
from stream_framework.feeds.notification_feed.redis import RedisNotificationFeed
from stream_framework.aggregators.base import NotificationAggregator
from stream_framework.verbs import register

from tastypie.models import ApiKey

from pin.models import Follow
# import json

# from django.core.serializers.json import DjangoJSONEncoder
# from waw.mqtt import user_publish

# from waw.api.v1.tools import push_activity_simple_json


class CreatePostVerb(Verb):
    id = 5
    infinitive = 'create'
    past_tense = 'created'


class CommentVerb(Verb):
    id = 6
    infinitive = 'comment'
    past_tense = 'commented'


class LikeVerb(Verb):
    id = 7
    infinitive = 'like'
    past_tense = 'liked'


class FollowVerb(Verb):
    id = 8
    infinitive = 'follow'
    past_tense = 'followed'


class RequestFollowVerb(Verb):
    id = 9
    infinitive = 'request follow'
    past_tense = 'requested follow'


class AcceptFollowVerb(Verb):
    id = 10
    infinitive = 'accept follow'
    past_tense = 'accepted follow'


register(CreatePostVerb)
register(CommentVerb)
register(LikeVerb)
register(FollowVerb)
register(RequestFollowVerb)
register(AcceptFollowVerb)


class MyAggregator(NotificationAggregator):

    '''
    Aggregates based on the same verb and object
    '''

    def get_group(self, activity):
        '''
        Returns a group based on the verb and object
        '''
        verb = activity.verb.id
        object_id = activity.object_id
        group = '%s-%s' % (verb, object_id)
        return group


class MyNotificationFeed(RedisNotificationFeed):
    key_format = 'feed:notification:%(user_id)s'
    aggregator_class = MyAggregator


class UserNotification(object):
    User_id = None

    def __init__(self, user_id):
        try:
            api_key = ApiKey.objects.only('user', 'key').get(user_id=user_id)
        except Exception as e:
            print str(e)
            api_key = None

        self.User_id = user_id
        if api_key:
            self.token = api_key.key

    def create_activity(self, actor, verb, object_id, target, time, extra_context=None):
        if extra_context:
            activity = Activity(actor, verb, object_id, target, time, extra_context)
        else:
            activity = Activity(actor, verb, object_id, target, time)
        return activity

    def get_user_follower_ids(self, user_id):
        ids = Follow.objects.filter(target=user_id).values_list('user_id', flat=True)
        return ids

    def get_obj_notif(self, before):
        feed = MyNotificationFeed(self.User_id)
        try:
            notification = feed.order_by('-activity_id')[before: before + 10]
        except Exception as e:
            print str(e)
            notification = None

        return notification

    def like_post(self, actor, object_id, create_time):
        try:
            feed = MyNotificationFeed(self.User_id)
            activity = self.create_activity(actor=actor, verb=LikeVerb,
                                            object_id=object_id, target=self.User_id,
                                            time=create_time)
            feed.add(activity)

            # ''' push notification '''
            # to_json = json.dumps(push_activity_simple_json(activity=activity),
            #                      cls=DjangoJSONEncoder)

            # if self.username and self.topic and self.token:
            #     user_publish(username=self.username, text=to_json,
            #                  token=self.token, topic=self.topic)

        except Exception as e:
            print str(e), ",notification, like_post function"

    def dislike_post(self, actor, object_id, create_time):
        try:
            feed = MyNotificationFeed(self.User_id)
            activity = self.create_activity(actor=actor, verb=LikeVerb,
                                            object_id=object_id, target=self.User_id,
                                            time=create_time)
            feed.remove(activity)
        except Exception, e:
            print str(e), ",notification, dislike_post function"

    def add_post(self, post_id, post_owner_id, post_create_at):
        try:
            feed = MyNotificationFeed(self.User_id)
            activity = self.create_activity(actor=post_owner_id, verb=CreatePostVerb,
                                            object_id=post_id, target=self.User_id,
                                            time=post_create_at)
            feed.add(activity)
        except Exception as e:
            print str(e), ",notification, add_post function"

    def delete_post(self, post_id, post_owner_id, post_create_at):
        try:
            feed = MyNotificationFeed(self.User_id)
            activity = self.create_activity(actor=post_owner_id, verb=CreatePostVerb,
                                            object_id=post_id, target=self.User_id,
                                            time=post_create_at)
            feed.remove(activity)
        except Exception as e:
            print str(e), ",notification, delete_post function"

    def add_comment(self, actor, object_id, create_time, text):
        try:
            feed = MyNotificationFeed(self.User_id)
            activity = self.create_activity(actor=actor, verb=CommentVerb,
                                            object_id=object_id, target=self.User_id,
                                            time=create_time,
                                            extra_context=dict(text=text))
            feed.add(activity)

            # ''' push notification '''
            # to_json = json.dumps(push_activity_simple_json(activity=activity),
            #                      cls=DjangoJSONEncoder)
            # if self.username and self.topic and self.token:
            #     user_publish(username=self.username, text=to_json,
            #                  token=self.token, topic=self.topic)

        except Exception, e:
            print str(e), ",notification, add_comment function"

    def delete_comment(self, actor, object_id, create_time):
        try:
            feed = MyNotificationFeed(self.User_id)
            activity = self.create_activity(actor=actor, verb=CommentVerb,
                                            object_id=object_id, target=self.User_id,
                                            time=create_time)
            feed.remove(activity)
        except Exception, e:
            print str(e), ",notification, delete_comment function"

    def follow(self, actor, object_id, create_time):
        try:
            feed = MyNotificationFeed(self.User_id)
            activity = self.create_activity(actor=actor, verb=FollowVerb,
                                            object_id=object_id, target=self.User_id,
                                            time=create_time)
            feed.add(activity)

            # ''' push notification '''
            # to_json = json.dumps(push_activity_simple_json(activity=activity),
            #                      cls=DjangoJSONEncoder)
            # if self.username and self.topic and self.token:
            #     user_publish(username=self.username, text=to_json,
            #                  token=self.token, topic=self.topic)

        except Exception, e:
            print str(e), ",notification, follow function"

    def request_follow(self, actor, object_id, create_time):
        try:
            feed = MyNotificationFeed(self.User_id)
            activity = self.create_activity(actor=actor, verb=RequestFollowVerb,
                                            object_id=object_id, target=self.User_id,
                                            time=create_time)
            feed.add(activity)

            # ''' push notification '''
            # to_json = json.dumps(push_activity_simple_json(activity=activity),
            #                      cls=DjangoJSONEncoder)
            # if self.username and self.topic and self.token:
            #     user_publish(username=self.username, text=to_json,
            #                  token=self.token, topic=self.topic)

        except Exception, e:
            print str(e), ",notification, request_follow function"

    def accept_follow(self, actor, object_id, create_time):
        try:
            feed = MyNotificationFeed(self.User_id)
            activity = self.create_activity(actor=actor, verb=AcceptFollowVerb,
                                            object_id=object_id, target=self.User_id,
                                            time=create_time)
            feed.add(activity)

            # ''' push notification '''
            # to_json = json.dumps(push_activity_simple_json(activity=activity),
            #                      cls=DjangoJSONEncoder)
            # if self.username and self.topic and self.token:
            #     user_publish(username=self.username, text=to_json,
            #                  token=self.token, topic=self.topic)

        except Exception, e:
            print str(e), ",notification, accept_follow function"

    def unfollow(self, actor, object_id, create_time):
        try:
            feed = MyNotificationFeed(self.User_id)
            activity = self.create_activity(actor=actor, verb=FollowVerb,
                                            object_id=object_id, target=self.User_id,
                                            time=create_time)
            feed.remove(activity)
        except Exception, e:
            print str(e), ",notification, unfollow function"


# feed = MyNotificationFeed(38)
# activity = Activity(actor=38, verb=CommentVerb, object=38, target=38, time=datetime.utcnow())
# feed.add(activity)
# print feed[:5]
