from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from shop.models import Product, Cart
from shop.forms import ReciversForm


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


def form(request):
    return render(request, 'shop/form.html')
