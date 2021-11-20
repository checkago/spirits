from django import views
from .models import Cart, Customer
from django.core.exceptions import PermissionDenied


class CartMixin(views.generic.detail.SingleObjectMixin, views.View):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            customer = Customer.objects.filter(user=request.user).first()
            if not customer:
                customer = Customer.objects.create(
                    user=request.user
                )
            cart = Cart.objects.filter(owner=customer, in_order=False).first()
            if not cart:
                cart = Cart.objects.create(owner=customer)
        else:
            cart = Cart.objects.filter(for_anonymous_user=True).first()
            if not cart:
                cart = Cart.objects.create(for_anonymous_user=True)
        self.cart = cart
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart'] = self.cart
        return context


class OwnershipMixin(object):
    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs
        # we need to manually "wake up" self.request.user which is still a SimpleLazyObject at this point
        # and manually obtain this object's owner information.
        current_user = self.request.user._wrapped if hasattr(self.request.user, '_wrapped') else self.request.user
        object_owner = getattr(self.get_object(), 'customer')

        if current_user != object_owner and not current_user.is_superuser and not current_user.is_staff:
            raise PermissionDenied
        return super(OwnershipMixin, self).dispatch(request, *args, **kwargs)
