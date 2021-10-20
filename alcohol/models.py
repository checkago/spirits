import email

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import  reverse
from django.utils import timezone
from django.utils.safestring import mark_safe

from utils import upload_function


class BottleVolume(models.Model):
    name = models.CharField(max_length=11, verbose_name='Объем тары')

    class Meta:
        verbose_name = 'Объем тары'
        verbose_name_plural = 'Объемы тары'

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Категория')
    slug = models.SlugField(unique=True, verbose_name='Псевдоним/Slug')

    class Meta:
        verbose_name = 'Категория товара'
        verbose_name_plural = 'Категории товаров'

    def __str__(self):
        return self.name


    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'category_slug': self.slug})


class Brand(models.Model):
    name = models.CharField(max_length=100, verbose_name='Торговая марка')
    slug = models.SlugField(unique=True, verbose_name='Псевдоним/Slug')
    category = models.ManyToManyField(Category, related_name='brands', verbose_name='Категории')
    since_date = models.DateField(verbose_name='Дата основания')
    country = models.ForeignKey('Country', on_delete=models.CASCADE, verbose_name='Страна происхождения')
    description = models.TextField(verbose_name='Описание', default='Описание появится позже')
    products = models.ManyToManyField('Product', blank=True, related_name='products', verbose_name='Продукты')
    image = models.ImageField(upload_to=upload_function)

    class Meta:
        verbose_name = 'Торговая марка'
        verbose_name_plural = 'Бренды'

    def __str__(self):
        return f"{self.name} | {self.country.name}"

    def get_absolute_url(self):
        return reverse('brand_detail', kwargs={'brand_slug': self.slug})


class Product(models.Model):
    name = models.CharField(max_length=150, verbose_name='Наименование')
    slug = models.SlugField(unique=True, verbose_name='Псевдоним/Slug')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, verbose_name='Бренд')
    volume = models.ForeignKey(BottleVolume, on_delete=models.CASCADE, verbose_name='Объем')
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Цена')
    stock = models.IntegerField(default=1, verbose_name='Количество на складе')
    description = models.TextField(default='Описание товара появится позже', verbose_name='Описание товара')
    recipe = models.ForeignKey('Recipe', blank=True, null=True, on_delete=models.CASCADE, verbose_name='Рецепт')
    offer_of_the_week = models.BooleanField(default=False, verbose_name='Предложение недели')
    image = models.ImageField(upload_to=upload_function)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return f"{self.brand.name} | {self.name} | {self.volume.name} | {self.category.name}"

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'category_slug': self.category.slug, 'brand_slug': self.brand.slug,
                                                 'product_slug': self.slug})

    @property
    def ct_model(self):
        return self._meta.model.name


class Country(models.Model):
    name = models.CharField(max_length=100, verbose_name='Страна')
    slug = models.SlugField(unique=True, verbose_name='Псевдоним/Slug')

    class Meta:
        verbose_name = 'Страна'
        verbose_name_plural = 'Страны производителей'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=150, verbose_name='Наименование рецепта')
    products = models.ManyToManyField(Product, related_name='recipes', verbose_name='Напитки используемые для рецепта')
    description = models.TextField(verbose_name='Описание рецепта')

    class Meta:
        verbose_name = 'Рецепт напитка/коктейля'
        verbose_name_plural = 'Рецепты напитков/коктейлей'

    def __str__(self):
        return self.name


class CartProduct(models.Model):
    user = models.ForeignKey('Customer', on_delete=models.CASCADE, verbose_name='Покупатель')
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE, verbose_name='Корзина')
    volume = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name='Объем')
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('volume', 'object_id')
    qty = models.PositiveIntegerField(default=1, verbose_name='Количество')
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая стоимость')

    class Meta:
        verbose_name = 'Продукт корзины'
        verbose_name_plural = 'Продукты корзины'

    def __str__(self):
        return f"Продукт: {self.content_object.name} для корзины"

    def save(self, *args, **kwargs):
        self.final_price = self.qty * self.content_object.price
        super().save(*args, **kwargs)


class Cart(models.Model):
    owner = models.ForeignKey('Customer', on_delete=models.CASCADE, verbose_name='Покупатель')
    products = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart',
                                      verbose_name='Товары в корзине')
    total_products = models.IntegerField(default=0, verbose_name='Общее кол-во товаров в корзине')
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая стоимость')
    in_order = models.BooleanField(default=False)
    for_anonimous_user = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины покупателей'

    def __str__(self):
        return f"{self.id} | {self.owner.name} | {self.final_price}"


class Order(models.Model):

    STATUS_NEW = 'new'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'ready'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'

    BYING_TYPE_SELF = 'self'
    BYING_TYPE_DELIVERY = 'delivery'

    STATUS_CHOICES = (
        (STATUS_NEW, 'Новый заказ'),
        (STATUS_CONFIRMED, 'Заказ подтвержден'),
        (STATUS_IN_PROGRESS, 'Заказ в обработке'),
        (STATUS_READY, 'Заказ готов'),
        (STATUS_COMPLETED, 'Заказ получен покупателем'),
        (STATUS_CANCELLED, 'Заказ отменен')
    )

    BYING_TYPE_CHOICES = (
        (BYING_TYPE_SELF, 'Самовывоз из магазина'),
        (BYING_TYPE_DELIVERY, 'Доставка')
    )

    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='orders', verbose_name='Покупатель')
    first_name = models.CharField(max_length=255, verbose_name='Имя')
    last_name = models.CharField(max_length=255, verbose_name='Фамилия')
    phone = models.CharField(max_length=18, verbose_name='Номер телефона')
    cart = models.ForeignKey(Cart, on_delete=models. CASCADE, verbose_name='Корзина')
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default=STATUS_NEW)
    bying_type = models.CharField(max_length=100, choices=BYING_TYPE_CHOICES, default=BYING_TYPE_DELIVERY)
    comment = models.TextField(blank=True, null=True, verbose_name='Комментарий к заказу')
    created_at = models.DateField(auto_now=True, verbose_name='дата создания заказа')
    order_date = models.DateField(default=timezone.now, verbose_name='Предпочитаемая дата получения заказа')

    class Meta:
        verbose_name = 'Заказ покупателя'
        verbose_name_plural = 'Заказы покупателей'

    def __str__(self):
        return f"MS-000{self.id}"


class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    is_active = models.BooleanField(default=True, verbose_name='Активный')
    phone = models.CharField(max_length=18, verbose_name='Номер телефона')
    addresses = models.ManyToManyField('Address', blank=True, related_name='addresses', verbose_name='Адрес покупателя')
    user_orders = models.ManyToManyField(Order, blank=True, related_name='related_customer', verbose_name='Заказы покупателя')
    wishlist = models.ManyToManyField(Product, blank=True, verbose_name='Лист ожидания')

    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Список покупателей'

    def __str__(self):
        return f"{self.user.username}"


class Address(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, verbose_name='Покупатель')
    city = models.CharField(max_length=50, verbose_name='Город')
    metro = models.CharField(max_length=50, blank=True, null=True, verbose_name='ст. Метро')
    street = models.CharField(max_length=300, verbose_name='Улица, дом, подъезд, квартира')
    primary = models.BooleanField(default=True, verbose_name='Основной адрес?')

    class Meta:
        verbose_name = 'Адрес покупателя'
        verbose_name_plural = 'Адреса покупателей'

    def __str__(self):
        return f"Адрес покупателя {self.customer.user.username} | {self.city}, {self.metro}, {self.street}"


class Notification(models.Model):
    recipient = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='Получатель уведомления')
    text = models.TextField(verbose_name='Текст уведомления')
    read = models.BooleanField(default=False, verbose_name='Прочитано')

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления для пользователей'

    def __str__(self):
        return f"Уведомление для {self.recipient.user.username} | {self.id}"


class ImageGallery(models.Model):

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    image = models.ImageField(upload_to=upload_function)
    use_in_slider = models.BooleanField(default=False, verbose_name='Использовать в слайдере')

    class Meta:
        verbose_name = 'Галерея изображений'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"Изображение для {self.content_object}"

    def image_url(self):
        return mark_safe(f'<img src="{self.image.url}" width="auto" height="100px"')













