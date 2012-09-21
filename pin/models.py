from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    #title = models.CharField(max_length=250, blank=True)
    text = models.TextField(blank=True)
    image = models.CharField(max_length=500)
    create_date = models.DateField(auto_now_add=True)
    create = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User)
    like = models.IntegerField(default=0)
    
    def __unicode__(self):
        return self.title
    
    