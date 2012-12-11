from django.contrib import admin
from pin.models import Post

class PinAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', )

admin.site.register(Post, PinAdmin)