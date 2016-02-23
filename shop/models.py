# -*- coding: utf-8 -*-
from django.db import models

from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class Category(models.Model):
    name = models.CharField(max_length=150)
    text = models.TextField()

    def __unicode__(self):
        return self.name


class Product(models.Model):
    X1 = 1
    X2 = 2
    H2 = 3
    X2H2 = 4

    MODES = (
        (X1, "normal"),
        (X2, "x2"),
        (H2, "H2"),
        (X2H2, "X2H2"),
    )
    title = models.CharField(max_length=250)
    title_en = models.CharField(max_length=250, blank=True, default="")
    description = models.TextField()
    price = models.IntegerField(default=0)
    in_stock = models.BooleanField(default=True)
    in_home = models.BooleanField(default=False)
    sort = models.IntegerField(default=0)

    mode = models.IntegerField(choices=MODES, default=X1)

    category = models.ForeignKey(Category)

    def __unicode__(self):
        return self.title

    def delete(self, *args, **kwargs):
        super(Product, self).delete(*args, **kwargs)


class ProductImages(models.Model):
    image = models.ImageField(upload_to="product")
    primary = models.BooleanField(default=False)
    product = models.ForeignKey(Product, related_name="images")

    def delete(self, *args, **kwargs):
        storage, path = self.image.storage, self.image.path
        super(ProductImages, self).delete(*args, **kwargs)
        storage.delete(path)


class Cart(models.Model):
    quantity = models.IntegerField(default=1)
    product = models.ForeignKey(Product)
    user = models.ForeignKey(User)


class Recivers(models.Model):
    full_name = models.CharField(max_length=300)
    address = models.TextField()
    phone = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=100)

    user = models.ForeignKey(User)


class Order(models.Model):
    CHECKING = 1
    ACCEPTED = 2
    PREPAIRING = 3
    SENT = 4
    RECIVED = 5

    STATUS = (
        (CHECKING, _("Pending")),
        (ACCEPTED, _("Accepted")),
        (PREPAIRING, _("Preparation")),
        (SENT, _("Sent")),
        (RECIVED, _("Recived")),
    )

    product = models.ForeignKey(Product)
    quantity = models.IntegerField(default=1)
    status = models.IntegerField(choices=STATUS, default=CHECKING)

    user = models.ForeignKey(User)
    reciver = models.ForeignKey(Recivers)
