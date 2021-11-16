from django import forms
from ckeditor.widgets import CKEditorWidget
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


class RecipeAdminForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget(config_name='awesome_ckeditor'))

    class Meta:
        verbose_name = 'Описание'
        model = Recipe
        fields = '__all__'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    form = RecipeAdminForm


class SliderAdminForm(forms.ModelForm):
    text = forms.CharField(widget=CKEditorWidget(config_name='awesome_ckeditor'))

    class Meta:
        verbose_name = 'Описание'
        model = Slider
        fields = '__all__'


@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    list_display = ('name',)
    form = SliderAdminForm


class ArticleAdminForm(forms.ModelForm):
    text = forms.CharField(widget=CKEditorWidget(config_name='awesome_ckeditor'))

    class Meta:
        verbose_name = 'Текст'
        model = Article
        fields = '__all__'


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title',)
    form = ArticleAdminForm


admin.site.register(BottleVolume)
admin.site.register(CartProduct)
admin.site.register(Order)
admin.site.register(Cart)
admin.site.register(Customer)
admin.site.register(Address)
admin.site.register(Notification)
admin.site.register(ImageGallery)
admin.site.register(Baner)
admin.site.register(Review)
