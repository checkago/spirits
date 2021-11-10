import brand as brand
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render
from django import views
from django.contrib import messages
from django.views.generic import DetailView
from django.http import HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import authenticate, login
from .forms import LoginForm, RegistrationForm, OrderForm
from .mixins import CartMixin
from .models import CartProduct, Category, Customer, Product, Brand, Slider, BottleVolume
from utils.recalc_cart import recalc_cart


class IndexView(CartMixin, views.View):

    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        sliders = Slider.objects.all()
        products = Product.objects.all()
        context = {
            'categories': categories,
            'products': products,
            'sliders': sliders,
            'cart': self.cart
        }
        return render(request, 'index.html', context)


class CategoryView(CartMixin, views.View):
    model = Category
    categories = Category.objects.all()
    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        products = Product.objects.all()
        volumes = BottleVolume.objects.all()
        brands = Brand.objects.all()
        context = {
            'categories': categories,
            'products': products,
            'volumes': volumes,
            'brands': brands,
            'cart': self.cart
        }
        return render(request, 'category/categories.html', context)


class CategoryDetailView(CartMixin, views.generic.DetailView):
    model = Category
    categories = Category.objects.all()
    brands = Brand.objects.all()
    volumes = BottleVolume.objects.all()
    template_name = 'category/category_detail.html'
    slug_url_kwarg = 'category_slug'
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('search')
        category = self.get_object()
        context['cart'] = self.cart
        context['volumes'] = BottleVolume.objects.all()
        context['brands'] = Brand.objects.all()
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


class BrandsView(CartMixin, views.View):
    model = Brand
    categories = Category.objects.all()
    def get(self, request, *args, **kwargs):
        brands = Brand.objects.all()
        context = {
            'brands': brands,
            'cart': self.cart
        }
        return render(request, 'brands/brands.html', context)


class ProductDetailView(CartMixin, views.generic.DetailView):
    model = Product
    template_name = 'product/product_detail.html'
    slug_url_kwarg = 'product_slug'
    title = 'product_name'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ct_model = self.model().ct_model
        context['cart'] = self.cart
        context['ct_model'] = ct_model
        context['categories'] = Category.objects.all()
        return context


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
        orders = Customer.user_orders.all()
        context = {
            'success': customer,
            'orders': orders,
            'cart': self.cart
        }
        return render(request, 'auth/account_view.html', context)


class CartView(CartMixin, views.View):

    def get(self, request, *args, **kwargs):
        return render(request, 'cart/cart.html', {'cart': self.cart})


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


class CheckoutView(CartMixin, views.View):

    def get(self, request, *args, **kwargs):
        customer = Customer.objects.get(user=request.user)
        categories = Category.objects.all()
        form = OrderForm(request.POST or None)
        context = {
            'cart': self.cart,
            'categories': categories,
            'customer': customer,
            'form': form
        }
        return render(request, 'cart/checkout.html', context)


class MakeOrderView(CartMixin, views.View):

    def post(self, request, *args, **kwargs):
        form = OrderForm(request.POST or None)
        customer = Customer.objects.get(user=request.user)
        if form.is_valid():
            new_order = form.save(commit=False)
            new_order.customer = customer
            new_order.first_name = form.cleaned_data['first_name']
            new_order.last_name = form.cleaned_data['last_name']
            new_order.phone = form.cleaned_data['phone']
            new_order.address = form.cleaned_data['address']
            new_order.buying_type = form.cleaned_data['buying_type']
            new_order.order_date = form.cleaned_data['order_date']
            new_order.comment = form.cleaned_data['comment']
            new_order.save()
            self.cart.in_order = True
            self.cart.save()
            new_order.cart = self.cart
            new_order.save()
            customer.orders.add(new_order)
            messages.add_message(request, messages.INFO, 'Спасибо за заказ! Менеджер с Вами свяжется')
            return HttpResponseRedirect('/')
        return HttpResponseRedirect('/checkout/')


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
        messages.add_message(request, messages.INFO, "Товар удален из корзины")
        return HttpResponseRedirect(request.META['HTTP_REFERER'])


class ChangeQTYView(CartMixin, views.View):

    def post(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model='product')
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





