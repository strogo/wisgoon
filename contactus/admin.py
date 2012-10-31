from django.contrib import admin
from contactus.models import Feedback

class FeedbackAdmin(admin.ModelAdmin):
    list_display=('name','email','text','website')

admin.site.register(Feedback, FeedbackAdmin)
