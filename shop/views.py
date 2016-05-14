# import requests
# import json

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

# from datetime import datetime, timedelta
from shop.models import Product, Cart
from shop.forms import ReciversForm

# from pin.api6.http import return_json_data, return_not_found
from django.views.decorators.csrf import csrf_exempt


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
@csrf_exempt
def form(request):
    # reciver = None
    # if request.method == "POST":
    #     form = OrderForm(request.POST)
    #     if form.is_valid():
    #         try:
    #             reciver = Recivers.objects.get(user=request.user)
    #             reciver.full_name = request.POST.get('first_name') + request.POST.get('last_name')
    #             reciver.address = request.POST.get('address')
    #             reciver.phone = request.POST.get('phone')
    #             reciver.postal_code = request.POST.get('postal_code')
    #             reciver.save()
    #         except:
    #             full_name = request.POST.get('first_name') + request.POST.get('last_name')
    #             reciver = Recivers.objects.create(full_name=full_name,
    #                                               address=request.POST.get('address'),
    #                                               phone=request.POST.get('phone'),
    #                                               postal_code=request.POST.get('postal_code'),
    #                                               user=request.user)
    #         product_id = int(request.POST.get('product_id'))
    #         try:
    #             Product.objects.get(id=product_id)
    #         except Exception as e:
    #             return render(request, 'shop/payment_error.html', {
    #                 'message': str(e)
    #             })

    #         Order.objects.create(product_id=product_id,
    #                              quantity=request.POST.get('quantity'),
    #                              user=request.user,
    #                              reciver=reciver)

            # if create_customers(request.user):
    return render(request, 'shop/form.html')


# def authorization(request):
#     status = True
#     payload = {'client_id': '5731e808-899c-4504-ac8e-140e2e65ec48',
#                'response_type': 'code', 'scope': 'write', 'access_type': 'offline',
#                'redirect_uri': 'http://www.wisgoon.com/shop/hesabit/redirect'}

#     url = 'https://www.hesabit.com/oauth2/authorize'
#     request = requests.get(url, params=payload, headers={'Content-Type': 'application/json'})
#     if int(request.status_code) != 200:
#         status = False
#     return status


# def get_access_token(request):
#     client_id = '5731ed48-6898-4b38-ad3a-15b42e65ec48'
#     client_secret = '5731ed48-b9d8-4374-91eb-15b42e65ec48'
#     token_json = None
#     request_token = None

#     code = request.GET.get('code', False)
#     if code:
#         payload = {
#             'grant_type': 'authorization_code',
#             'code': code,
#             'redirect_uri': 'http://127.0.0.1:8000/shop/hesabit/redirect',
#             'client_id': client_id,
#             'client_secret': client_secret
#         }

#         request_token = requests.post('https://api.hesabit.com/oauth2/token', data=payload)
#         token_json = json.loads(request_token.content)
#     else:
#         token_json = json.loads(request.body)

#     try:
#         # 1680216
#         api_key, created = HesabitToken.objects.get_or_create(user_id=5)
#     except Exception as e:
#         return render(request, 'shop/payment_error.html', {'message': str(e)})

#     api_key.token = token_json['access_token']
#     api_key.refresh_token = token_json['refresh_token']
#     api_key.create_at = datetime.now()
#     api_key.save()

#     return return_json_data({'token': token_json})


# def refresh_token(refresh_token):
#     client_id = '5731ed48-6898-4b38-ad3a-15b42e65ec48'
#     client_secret = '5731ed48-b9d8-4374-91eb-15b42e65ec48'

#     payload = {
#         'grant_type': 'refresh_token',
#         'client_id': client_id,
#         'client_secret': client_secret,
#         'refresh_token': refresh_token
#     }

#     request_token = requests.post('https://api.hesabit.com/oauth2/token', data=payload)
#     token_json = json.loads(request_token.content)

#     try:
#         # 1680216
#         api_key, created = HesabitToken.objects.get_or_create(user_id=5)
#     except:
#         return return_not_found()

#     api_key.token = token_json['access_token']
#     api_key.refresh_token = token_json['refresh_token']
#     api_key.create_at = datetime.now()
#     api_key.save()

#     return token_json


# def create_customers(user):
#     status = True

#     payload = {
#         'name': user.recivers.full_name,
#         'email': user.email,
#         'mobile': user.recivers.phone,
#         'address': user.recivers.address,
#     }

#     try:
#         api_key = HesabitToken.objects.get_or_create(user_id=5)
#     except Exception as e:
#         print str(e)

#     if api_key.create_at > datetime.now() - timedelta(hours=10):
#         url = 'https://api.hesabit.com/v1/customers/?access_token={}'.format(api_key.token),
#     else:
#         token = refresh_token(api_key.refresh_token)
#       url = 'https://api.hesabit.com/v1/customers/?access_token={}'.format(token['access_token']),

#     request_token = requests.post(url, data=payload)
#     if int(request_token.status_code) != 200:
#         status = False

#     return status
