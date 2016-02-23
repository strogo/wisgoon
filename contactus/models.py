# encoding: utf-8
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Feedback(models.Model):
    name = models.CharField(max_length=250, blank=True, verbose_name=_("Name"))
    email = models.EmailField(verbose_name=_("Email"), blank=True)
    website = models.URLField(verbose_name=_("Website"), blank=True)
    text = models.TextField(verbose_name=_("Message"))
