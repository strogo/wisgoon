from django.forms.models import ModelForm
from rss.models import Feed,Report

class FeedForm(ModelForm):
    class Meta:
        model=Feed
        exclude = ('title','priority', 'creator', 'followers','view','status')
        
class ReportForm(ModelForm):
    class Meta:
        model=Report
        exclude = ('user','item')