from user_profile.models import Profile
from django.forms import ModelForm

class ProfileForm(ModelForm):
    class Meta:
        model=Profile
        exclude=('user','cnt_post','cnt_like','score','count_flag','trusted')
