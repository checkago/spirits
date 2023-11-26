from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import *


urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('accounts/login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('account/', AccountView.as_view(), name='account'),
    path('cart/', CartView.as_view(), name='cart'),
    path('add-to-cart/<str:ct_model>/<str:slug>/', AddToCartView.as_view(), name='add_to_cart'),
    path('remove-from-cart/<str:ct_model>/<str:slug>/', DeleteFromCartView.as_view(), name='delete_from_cart'),
    path('change-qty/<str:ct_model>/<str:slug>/', ChangeQTYView.as_view(), name='change_qty'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('make-order/', MakeOrderView.as_view(), name='make_order'),
    path('checkout-complete/', CheckoutCompleteView.as_view(), name='checkout-complete'),
    path('catalog/', CategoryView.as_view(), name='categories'),
    path('brands/brands/', BrandsView.as_view(), name='brands'),
    path('clear-notifications/', ClearNotificationsView.as_view(), name='clear-notifications'),
    path('account/orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('add-to-wishlist/<int:product_id>/', AddToWishlistView.as_view(), name='add_to_wishlist'),
    path('remove-from-wishlist/<int:product_id>/', RemoveFromWishlistView.as_view(), name='remove_from_wishlist'),
    path('<str:category_slug>/', CategoryDetailView.as_view(), name='category_detail'),
    path('<str:category_slug>/<str:brand_slug>/<str:product_slug>/', ProductDetailView.as_view(), name='product_detail'),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

