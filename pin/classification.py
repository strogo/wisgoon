# -*- coding: utf-8 -*-
from textblob import TextBlob
from textblob.classifiers import NaiveBayesClassifier
from django.core.cache import cache
from pin.models import CommentClassification
from pin.classification_tools import normalize

cl = cache.get(CommentClassification.CACHE_NAME)
if not cl:
    train = []
    for cc in CommentClassification.objects.all():
        txt = u"%s" % cc.get_text()
        train.append((txt, cc.tag_id))

    cl = NaiveBayesClassifier(train)
    cache.set(CommentClassification.CACHE_NAME, cl, 30)


def get_comment_category(sentence):
    sentence = normalize(sentence)
    blob = TextBlob(sentence, classifier=cl)
    try:
        cname = blob.classify()
    except Exception, e:
        print str(e)
        cname = 0
    return cname
