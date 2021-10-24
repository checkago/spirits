from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django import views
from django.contrib import messages
from django.views.generic import DetailView
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm, RegistrationForm
from .mixins import CartMixin
from .models import Product, Category, Customer, CartProduct
from utils.recalc_cart import recalc_cart


class IndexView(views.View):
    def get(self, request, *args, **kwargs):
        return render(request, 'index.html', {})


class CategoryDetailView(CartMixin, views.generic.DetailView):
    model = Category
    template_name = 'category/category_detail.html'
    slug_url_kwarg = 'category_slug'
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('search')
        category = self.get_object()
        context['cart'] = self.cart
        context['categories'] = self.model.objects.all()
        if not query and not self.request.GET:
            context['category_products'] = category.product_set.all()
            return context
        if query:
            products = category.product_set.filter(Q(title__icontains=query))
            context['category_products'] = products
            return context
        url_kwargs = {}
        for item in self.request.GET:
            if len(self.request.GET.getlist(item)) > 1:
                url_kwargs[item] = self.request.GET.getlist(item)
            else:
                url_kwargs[item] = self.request.GET.get(item)
        q_condition_queries = Q()
        for key, value in url_kwargs.items():
            if isinstance(value, list):
                q_condition_queries.add(Q(**{'value__in': value}), Q.OR)
            else:
                q_condition_queries.add(Q(**{'value': value}), Q.OR)
        pf = ProductFeatures.objects.filter(
            q_condition_queries
        ).prefetch_related('product', 'feature').values('product_id')
        products = Product.objects.filter(id__in=[pf_['product_id'] for pf_ in pf])
        context['category_products'] = products
        return context


class ProductDetailView(views.generic.DetailView):
    model = Product
    template_name = 'product/product_detail.html'
    slug_url_kwarg = 'product_slug'
    context_object_name = 'product'


# class AddToCartView(CartMixin, View):
#
#     def get(self, request, *args, **kwargs):
#         product_slug = kwargs.get('slug')
#         product = Product.objects.get(slug=product_slug)
#         cart_product, created = CartProduct.objects.get_or_create(
#             user=self.cart.owner, cart=self.cart, product=product
#         )
#         if created:
#             self.cart.products.add(cart_product)
#         recalc_cart(self.cart)
#         messages.add_message(request, messages.INFO, "Товар успешно добавлен")
#         return HttpResponseRedirect('/cart/')
#
#
# class DeleteFromCartView(CartMixin, View):
#
#     def get(self, request, *args, **kwargs):
#         product_slug = kwargs.get('slug')
#         product = Product.objects.get(slug=product_slug)
#         cart_product = CartProduct.objects.get(
#             user=self.cart.owner, cart=self.cart, product=product
#         )
#         self.cart.products.remove(cart_product)
#         cart_product.delete()
#         recalc_cart(self.cart)
#         messages.add_message(request, messages.INFO, "Товар успешно удален")
#         return HttpResponseRedirect('/cart/')
#
#
# class ChangeQTYView(CartMixin, View):
#
#     def post(self, request, *args, **kwargs):
#         product_slug = kwargs.get('slug')
#         product = Product.objects.get(slug=product_slug)
#         cart_product = CartProduct.objects.get(
#             user=self.cart.owner, cart=self.cart, product=product
#         )
#         qty = int(request.POST.get('qty'))
#         cart_product.qty = qty
#         cart_product.save()
#         recalc_cart(self.cart)
#         messages.add_message(request, messages.INFO, "Кол-во успешно изменено")
#         return HttpResponseRedirect('/cart/')
#
#
# class CartView(CartMixin, View):
#
#     def get(self, request, *args, **kwargs):
#         categories = Category.objects.all()
#         context = {
#             'cart': self.cart,
#             'categories': categories
#         }
#         return render(request, 'cart.html', context)


class LoginView(views.View):

    def get(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        context = {
            'form': form
        }
        return render(request, 'auth/login.html', context)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect('/')

        context = {
            'form': form
        }
        return render(request, 'auth/login.html', context)


class RegistrationView(views.View):

    def get(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST or None)
        context = {
            'form': form
        }
        return render(request, 'auth/registration.html', context)

    def post(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST or None)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.username = form.cleaned_data['username']
            new_user.email = form.cleaned_data['email']
            new_user.first_name = form.cleaned_data['first_name']
            new_user.last_name = form.cleaned_data['last_name']
            new_user.save()
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            Customer.objects.create(
                user=new_user,
                phone=form.cleaned_data['phone'],
            )
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            login(request, user)
            return HttpResponseRedirect('/')
        context = {
            'form': form
        }
        return render(request, 'auth/registration.html', context)


class AccountView(LoginRequiredMixin, CartMixin, views.View):

    def get(self, request, *args, **kwargs):
        customer = Customer.objects.get(user=request.user)
        context = {
            'success': customer,
            'cart': self.cart
        }
        return render(request, 'auth/account_view.html', context)


class AddToCartView(CartMixin, views.View):

    def get(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product, created = CartProduct.objects.get_or_create(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id
        )
        if created:
            self.cart.products.add(cart_product)
        recalc_cart(self.cart)
        messages.add_message(request, messages.INFO, "Товар успешно добавлен")
        return HttpResponseRedirect(request.META['HTTP_REFERER'])


class DeleteFromCartView(CartMixin, views.View):

    def get(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id
        )
        self.cart.products.remove(cart_product)
        cart_product.delete()
        recalc_cart(self.cart)
        messages.add_message(request, messages.INFO, "Товар удалнен из корзины")
        return HttpResponseRedirect(request.META['HTTP_REFERER'])


class ChangeQTYView(CartMixin, views.View):

    def get(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id
        )
        qty = int(request.POST.get('qty'))
        cart_product.qty = qty
        cart_product.save()
        recalc_cart(self.cart)
        messages.add_message(request, messages.INFO, "Кол-во товаров изменено")
        return HttpResponseRedirect(request.META['HTTP_REFERER'])







