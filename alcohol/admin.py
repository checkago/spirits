from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import *


class ImageGalleryInline(GenericTabularInline):
    model = ImageGallery
    readonly_fields = ('image_url',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ImageGalleryInline]


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ImageGalleryInline]


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(BottleVolume)
admin.site.register(Recipe)
admin.site.register(CartProduct)
admin.site.register(Order)
admin.site.register(Cart)
admin.site.register(Customer)
admin.site.register(Address)
admin.site.register(Notification)
admin.site.register(ImageGallery)
