from user_profile.models import Profile
from django.forms import ModelForm


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ('name', 'location', 'website', 'bio', 'avatar', 'jens')


class ProfileForm2(ModelForm):
    class Meta:
        model = Profile
        fields = ('name', 'location', 'website', 'bio', 'avatar', 'jens', 'cover')
