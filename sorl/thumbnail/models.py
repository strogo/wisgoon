from django.db import models
from sorl.thumbnail.conf import settings

from caching.base import CachingManager, CachingMixin

class KVStore(CachingMixin, models.Model):
    key = models.CharField(max_length=200, primary_key=True,
        db_column=settings.THUMBNAIL_KEY_DBCOLUMN
        )
    value = models.TextField()

    objects = CachingManager()
