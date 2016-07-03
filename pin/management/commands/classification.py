# -*- coding: utf-8 -*-

import ast
import sys

from sklearn import svm

from django.core.management.base import BaseCommand

from pin.models import UserActivitiesSample, UserActivities, UserLable

reload(sys)
sys.setdefaultencoding('utf8')


class Command(BaseCommand):
    def handle(self, *args, **options):
        user_activities = UserActivities.objects.only('activities', 'user').all()

        clf = svm.SVC(decision_function_shape='ovr', gamma=0.001, C=1000)
        sample_list, tag_list = get_sample()
        clf.fit(sample_list, tag_list)
        for user_activity in user_activities:

            lable = classification(clf, user_activity.activities)

            user_lable, created = UserLable.objects.get_or_create(user=user_activity.user)
            user_lable.lable = lable
            user_lable.save()
            # add_to_sample(user_activity)
            print "create user {} like activity".format(user_activity.user.id)


def get_sample():
    samples = UserActivitiesSample.objects.all()
    sample_list = []
    tag_list = []

    # ex [فرهنگی, سیاسی, ورزشی, مذهبی]
    for sample in samples:
        sample_list.append(ast.literal_eval(sample.array))
        tag_list.append(int(sample.lable.id))

    return sample_list, tag_list


def classification(clf, array):
    # clf = svm.SVC(gamma=0.001, C=100)
    array_like_cat = ast.literal_eval(array)
    if array_like_cat:
        result = clf.predict([array_like_cat])
        return result


# def add_to_sample(user_activity):
#     activities = ast.literal_eval(user_activity.activities)
#     try:
#         sample = UserActivitiesSample.objects.get(array=user_activity.activities)
#     except Exception, e:
#         sample = UserActivitiesSample.objects.create(array=user_activity.activities, lable=)
#     else:
#         pass
#     finally:
#         pass
#     if created:
#         for value, index in enumerate(activities):
#             if value != 0:
#                 UserLikeActivities.objects.create(score=value,
#                                                   category=int(index) + 1,
#                                                   user_activity=sample.id)
