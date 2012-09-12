from django.db import models

class Bank(models.Model):
    primary = models.IntegerField()
    block = models.TextField()
