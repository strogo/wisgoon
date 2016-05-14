from django.forms.models import ModelForm
from shop.models import Recivers
from django import forms


class ReciversForm(ModelForm):
    class Meta:
        model = Recivers
        fields = ('full_name', 'address', 'phone', 'postal_code')


class OrderForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    phone = forms.RegexField(r'^\?[0-9 .-]{8,11}$', required=True)
    address = forms.CharField(max_length=100, required=True)
    quantity = forms.IntegerField(min_value=1, required=True)
    price = forms.IntegerField(required=True)
    text = forms.CharField(widget=forms.Textarea)
