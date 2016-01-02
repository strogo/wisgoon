from django.contrib import admin

from models import Category, Product, ProductImages


class CategoryAdmin(admin.ModelAdmin):
    pass


class ProductImageInline(admin.TabularInline):
    model = ProductImages
    extra = 3


class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'category']
    inlines = [ProductImageInline, ]


class ProductImagesAdmin(admin.ModelAdmin):
    pass


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImages, ProductImagesAdmin)
