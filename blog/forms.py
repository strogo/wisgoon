from django import forms


class PostForm(forms.Form):
    title = forms.CharField(required=True)
    text = forms.CharField(widget=forms.Textarea)
    tags = forms.CharField()
    

class CommentForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)
    
