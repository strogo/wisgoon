#-*- coding: utf-8 -*-
from django.forms.models import ModelForm
from contactus.models import Feedback

from captcha.fields import CaptchaField


class FeedbackFrom(ModelForm):
    captcha = CaptchaField('کد امنیتی')

    class Meta:
        model = Feedback
