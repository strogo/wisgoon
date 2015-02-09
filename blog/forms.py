from django import forms
from ckeditor.widgets import CKEditorWidget


class PostForm(forms.Form):
    title = forms.CharField(required=True)
    abstract = forms.CharField(widget=CKEditorWidget())
    text = forms.CharField(widget=CKEditorWidget())
    tags = forms.CharField()
    

class CommentForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)
    
