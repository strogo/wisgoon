from django.forms.models import ModelForm
from contactus.models import Feedback

from captcha.fields import CaptchaField

class FeedbackFrom(ModelForm):
    captcha = CaptchaField()
    class Meta:
        model=Feedback
        
