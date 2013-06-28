from pin.forms import PinForm
from pin.models import Category

def pin_form(request):
    return { 'pin_form': PinForm }

def pin_categories(request):
    cats = Category.objects.all()

    return {'cats': cats}
