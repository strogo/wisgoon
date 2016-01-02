from django.conf.urls import patterns, include, url

urlpatterns = patterns('shop.views',
    url(r'^$', 'home', name='shop-home'),
    url(r'^product/(?P<product_id>\d+)$', 'product', name='shop-product'),
    url(r'^cart/add/product/$', 'cart_add_product', name='shop-cart-add-product'),
    url(r'^cart/remove/product/(?P<product_id>\d+)/$', 'cart_remove_product', name='shop-cart-remove-product'),
    url(r'^cart/$', 'cart', name='shop-cart'),
    url(r'^address/info/$', 'address', name='shop-address'),
)
