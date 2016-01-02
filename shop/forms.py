from django.forms.models import ModelForm
from shop.models import Recivers


class ReciversForm(ModelForm):
    class Meta:
        model = Recivers
        fields = ('full_name', 'address', 'phone', 'postal_code')
