import re

from haystack import indexes
from pin.models import Post, Comments
from user_profile.models import Profile

from pin.preprocessing import normalize_tags


class CommentIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True, stored=True)
    author = indexes.CharField(model_attr='user')

    def get_model(self):
        return Comments

    def index_queryset(self, using=None):
        return self.get_model().objects.all()


class PostIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    timestamp_i = indexes.IntegerField(model_attr='timestamp', stored=True)
    status_i = indexes.IntegerField(model_attr='status', stored=True)
    category_i = indexes.IntegerField(model_attr='category_id', stored=True)
    cnt_like_i = indexes.IntegerField(model_attr='cnt_like', stored=True)
    cnt_comment_i = indexes.IntegerField(model_attr='cnt_comment', stored=True)
    hash_s = indexes.CharField(model_attr='hash', stored=True)
    author = indexes.CharField(model_attr='user')
    tags = indexes.MultiValueField(indexed=True, stored=True)
    # pub_date = indexes.DateTimeField(model_attr='pub_date')

    def get_model(self):
        return Post

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()

    def prepare_tags(self, obj):
        hash_tags = re.compile(ur'(?i)(?<=\#)\w+', re.UNICODE)
        tags = hash_tags.findall(obj.text)
        nt = []
        for tag in tags:
            nt.append(normalize_tags(tag))
        # print nt
        return nt


class ProfileIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    status_i = indexes.IntegerField(model_attr='user__is_active', stored=True)
    score_i = indexes.IntegerField(model_attr='score', stored=True)
    author = indexes.CharField(model_attr='user')

    def get_model(self):
        return Profile

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()
