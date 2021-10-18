from django.shortcuts import render
from django import views

from .models import Product, Category, Brand


class IndexView(views.View):
    def get(self, request, *args, **kwargs):
        return render(request, 'index.html', {})


class CategoryDetailView(views.generic.DetailView):
    model = Category
    template_name = 'category/category_detail.html'
    slug_url_kwarg = 'category_slug'
    context_object_name = 'category'


class ProductDetailView(views.generic.DetailView):
    model = Product
    template_name = 'product/product_detail.html'
    slug_url_kwarg = 'product_slug'
    context_object_name = 'product'


