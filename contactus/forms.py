from django.forms.models import ModelForm
from contactus.models import Feedback

class FeedbackFrom(ModelForm):
    class Meta:
        model=Feedback
        
