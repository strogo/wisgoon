from django.db import models
from django.db.models.loading import get_model
from haystack import signals

# from models import Channel, Video
from pin.models import Post, Comments
from user_profile.models import Profile


class MySignalProcessor(signals.BaseSignalProcessor):
    def setup(self):
        models.signals.post_save.connect(self.handle_save, sender=Post)
        models.signals.post_save.connect(self.handle_save, sender=Profile)
        models.signals.post_save.connect(self.handle_save, sender=Comments)
        
        models.signals.post_delete.connect(self.handle_delete, sender=Post)
        models.signals.post_delete.connect(self.handle_delete, sender=Profile)
        models.signals.post_delete.connect(self.handle_delete, sender=Comments)
