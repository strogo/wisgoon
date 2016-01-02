#-*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=150)
    text = models.TextField()

    def __unicode__(self):
        return self.name


class Product(models.Model):
    NORMAL = 1
    SPECIAL = 2

    MODES = (
        (NORMAL, "normal"),
        (SPECIAL, "special"),
    )
    title = models.CharField(max_length=250)
    title_en = models.CharField(max_length=250, blank=True, default="")
    description = models.TextField()
    price = models.IntegerField(default=0)
    in_stock = models.BooleanField(default=True)

    mode = models.IntegerField(choices=MODES, max_length=30, default=NORMAL)

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
    postal_code = models.CharField(max_length=100, blank=True)

    user = models.ForeignKey(User)


class Order(models.Model):
    CHECKING = 1
    ACCEPTED = 2
    PREPAIRING = 3
    SENT = 4
    RECIVED = 5

    STATUS = (
        (CHECKING, u"در حال بررسی"),
        (ACCEPTED, u"تایید شد"),
        (PREPAIRING, u"در حال آماده سازی"),
        (SENT, u"ارسال گردید"),
        (RECIVED, u"به دست مشتری رسید"),
    )

    product = models.ForeignKey(Product)
    quantity = models.IntegerField(default=1)
    status = models.IntegerField(choices=STATUS, default=CHECKING)

    user = models.ForeignKey(User)
    reciver = models.ForeignKey(Recivers)
