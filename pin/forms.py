from django import forms
from django.forms.models import ModelForm
from pin.models import Post


class PinForm(ModelForm):
    class Meta:
        model=Post
        exclude = ('user', 'like', 'timestamp', 'status','device','hash',
        'actions','is_ads','view', 'show_in_default')
        
class PinDirectForm(forms.Form):
    image = forms.ImageField()
    description = forms.CharField(required=False)
    category = forms.IntegerField(required=True)
    
class PinUpdateForm(ModelForm):
    class Meta:
        model=Post
        exclude = ('user', 'like', 'timestamp',
        'image','status','device','hash', 'actions','view','show_in_default' )
        
