from pin.forms import PinForm

def pin_form(request):
    return { 'pin_form': PinForm }
