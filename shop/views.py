import requests
import json

from tastypie.models import ApiKey

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from shop.models import Product, Cart
from shop.forms import ReciversForm

from pin.api6.http import return_json_data, return_not_found


def home(request):
    products = Product.objects.filter(in_home=True).order_by('sort')
    return render(request, 'shop/home.html', {
        'products': products
    })


def product(request, product_id):
    prod = Product.objects.get(id=product_id)
    return render(request, 'shop/product.html', {
        'product': prod,
    })


@login_required
def cart_add_product(request):
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity'))
    if not product_id or not quantity:
        # raise error
        pass

    cart, created = Cart.objects.get_or_create(user=request.user,
                                               product_id=product_id)

    if created:
        cart.quantity = quantity
    else:
        cart.quantity = cart.quantity + quantity
    cart.save()

    return HttpResponseRedirect(reverse("shop-cart"))


@login_required
def cart_remove_product(request, product_id):
    Cart.objects.filter(user=request.user, product_id=product_id).delete()

    return HttpResponseRedirect(reverse("shop-cart"))


@login_required
def cart(request):
    total_price = 0
    cart_data = Cart.objects.filter(user=request.user)
    for cd in cart_data:
        total_price += cd.quantity * cd.product.price
    return render(request, 'shop/cart.html', {
        'cart': cart_data,
        'total_price': total_price,
    })


@login_required
def address(request):
    if request.method == "POST":
        form = ReciversForm(request.POST)
        if form.is_valid():
            model = form.save(commit=False)
            model.user = request.user
            model.save()
            return HttpResponseRedirect(reverse('shop-confirm'))
    else:
        form = ReciversForm()
    return render(request, 'shop/address.html', {
        'form': form,
    })


@login_required
def confirm(request):
    return render(request, 'shop/confirm.html')


@login_required
def form(request):
    return render(request, 'shop/form.html')


def authorization():
    status = True
    payload = {'client_id': '5731b82a-346c-4a37-8801-087d2e65ec48',
               'response_type': 'code', 'scope': 'write', 'access_type': 'offline',
               'redirect_uri': 'http://www.wisgoon.com/shop/hesabit/redirect'}

    url = 'https://www.hesabit.com/oauth2/authorize'
    request = requests.get(url, params=payload, headers={'Content-Type': 'application/json'})
    if int(request.status_code) != 200:
        status = False
    return status


def get_access_token(request):
    client_id = '5731b82a-346c-4a37-8801-087d2e65ec48'
    client_secret = '5731b82a-c364-48a7-8c87-087d2e65ec48'
    token_json = None
    request_token = None

    code = request.GET.get('code', False)
    if code:
        payload = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': 'http://www.wisgoon.com/shop/hesabit/redirect',
            'client_id': client_id,
            'client_secret': client_secret
        }

        request_token = requests.post('https://api.hesabit.com/oauth2/token', data=payload)
        token_json = json.loads(request_token.content)
    else:
        token_json = json.loads(request.body)

    try:
        api_key, created = ApiKey.objects.get_or_create(user_id=1680216)
    except:
        return return_not_found()

    api_key.key = token_json['access_token']
    api_key.save()

    return return_json_data({'token': token_json})
