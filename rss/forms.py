from django.forms.models import ModelForm
from rss.models import Feed

class FeedForm(ModelForm):
    class Meta:
        model=Feed
        exclude = ('title','priority', 'creator', 'followers','view','status')