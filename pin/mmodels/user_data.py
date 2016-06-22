from django.db import models
from django.conf import settings


class UserDataLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)


class UserData(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    province = models.CharField(max_length=250)
    city = models.CharField(max_length=250)
