#-*- coding: utf-8 -*-
from django.forms.models import ModelForm
from django.utils.translation import ugettext_lazy as _

from contactus.models import Feedback

from captcha.fields import CaptchaField


class FeedbackFrom(ModelForm):
    captcha = CaptchaField(_("Security code"))

    class Meta:
        model = Feedback
