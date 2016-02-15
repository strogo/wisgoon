from django.db import models

from haystack import signals

from pin.models import Post
from user_profile.models import Profile


class MySignalProcessor(signals.BaseSignalProcessor):
    def setup(self):
        models.signals.post_save.connect(self.handle_save, sender=Post)
        models.signals.post_save.connect(self.handle_save, sender=Profile)
        # models.signals.post_save.connect(self.handle_save, sender=Comments)

        models.signals.post_delete.connect(self.handle_delete, sender=Post)
        models.signals.post_delete.connect(self.handle_delete, sender=Profile)
        # models.signals.post_delete.connect(self.handle_delete, sender=Comments)
