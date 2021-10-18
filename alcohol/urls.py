from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from .views import IndexView, CategoryDetailView, ProductDetailView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('<str:category_slug>/', CategoryDetailView.as_view(), name='category_detail'),
    path('<str:category_slug>/<str:product_slug>/', ProductDetailView.as_view(), name='product_detail'),

]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

