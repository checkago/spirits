from django.conf import settings
from datetime import datetime
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
import operator
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.contrib.auth import get_user_model
from utils import upload_function

User = get_user_model()


class Slider(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    image = models.ImageField(upload_to=upload_function, verbose_name='Изображение')
    text = models.TextField(verbose_name='Текст')
    link = models.URLField(blank=True, null=True, verbose_name='Ссылка')
    active = models.BooleanField(default=True, verbose_name='Показывать на главной')

    class Meta:
        verbose_name = 'Слайд'
        verbose_name_plural = 'Слайдер'

        def __str__(self):
            return self.name


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
    image = models.ImageField(upload_to=upload_function, verbose_name='Маленький логотип')
    big_image = models.ImageField(upload_to=upload_function, blank=True, null=True, verbose_name='Большой логотип')

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
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Бренд')
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
        return f"{self.name} | {self.volume.name} | {self.category.name}"

    @property
    def ct_model(self):
        return self._meta.model_name

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'category_slug': self.category.slug, 'brand_slug': self.brand.slug,
                                                 'product_slug': self.slug})


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

    MODEL_CARTPRODUCT_DISPLAY_NAME_MAP = {
        "Product": {"is_constructable": True, "fields": ['name', 'brand.name'], "separator": '-'}
    }

    user = models.ForeignKey('Customer', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Покупатель')
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE, verbose_name='Корзина')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    qty = models.PositiveIntegerField(default=1, verbose_name='Количество')
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая стоимость')

    class Meta:
        verbose_name = 'Продукт корзины'
        verbose_name_plural = 'Продукты корзины'

    @property
    def display_name(self):
        model_fields = self.MODEL_CARTPRODUCT_DISPLAY_NAME_MAP.get(self.content_object.__class__._meta.model_name.capitalizer())
        if model_fields and model_fields['is_constructable']:
            display_name = model_fields['separator'].join(
                [operator.attrgetter(fied)(self.content_object) for fied in model_fields['fields']]
            )
            return display_name
        if model_fields and not model_fields['is_constructable']:
            display_name = operator.attrgetter(model_fields['field'])

    def __str__(self):
        return f"Продукт: {self.content_object} для корзины"

    def save(self, *args, **kwargs):
        self.final_price = self.qty * self.content_object.price
        super().save(*args, **kwargs)


class Cart(models.Model):
    owner = models.ForeignKey('Customer', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Покупатель')
    products = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart',
                                      verbose_name='Товары в корзине')
    total_products = models.IntegerField(default=0, verbose_name='Общее кол-во товаров в корзине')
    final_price = models.DecimalField(max_digits=9, decimal_places=2, default=0.00, verbose_name='Общая стоимость',
                                      null=True, blank=True)
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины покупателей'

    def __str__(self):
        return f"Корзина №{self.id} | Пользователь -  {self.owner}"


class Order(models.Model):

    STATUS_NEW = 'Новый'
    STATUS_CONFIRMED = 'Подтвержден'
    STATUS_IN_PROGRESS = 'В работе'
    STATUS_READY = 'Готов'
    STATUS_COMPLETED = 'Получен'
    STATUS_CANCELLED = 'Отменен'

    BYING_TYPE_SELF = 'Самовывоз из магазина'
    BYING_TYPE_DELIVERY = 'Доставка'

    STATUS_CHOICES = (
        (STATUS_NEW, 'Новый заказ'),
        (STATUS_CONFIRMED, 'Заказ подтвержден'),
        (STATUS_IN_PROGRESS, 'Заказ в обработке'),
        (STATUS_READY, 'Заказ готов'),
        (STATUS_COMPLETED, 'Заказ получен'),
        (STATUS_CANCELLED, 'Заказ отменен')
    )

    BYING_TYPE_CHOICES = (
        (BYING_TYPE_SELF, 'Самовывоз из магазина'),
        (BYING_TYPE_DELIVERY, 'Доставка')
    )

    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='orders', verbose_name='Покупатель')
    address = models.ForeignKey('Address', blank=True, null=True, on_delete=models.CASCADE, verbose_name='Адрес')
    first_name = models.CharField(max_length=255, verbose_name='Имя')
    last_name = models.CharField(max_length=255, verbose_name='Фамилия')
    phone = models.CharField(max_length=18, verbose_name='Номер телефона')
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True, verbose_name='Корзина')
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default=STATUS_NEW)
    buying_type = models.CharField(max_length=100, blank=True, null=True,
                                   choices=BYING_TYPE_CHOICES,
                                   default=BYING_TYPE_DELIVERY, verbose_name='Тип покупки')
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
    birth_date = models.DateField(blank=True, null=True, verbose_name='Дата рождения')
    user_addresses = models.ManyToManyField('Address', blank=True, related_name='addresses', verbose_name='Адрес покупателя')
    user_orders = models.ManyToManyField(Order, blank=True, related_name='related_customer', verbose_name='Заказы покупателя')
    wishlist = models.ManyToManyField(Product, blank=True, verbose_name='Лист ожидания')

    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Список покупателей'

    @property
    def age(self):
        return int((datetime.now().date() - self.birth_date).days / 365.25)

    @property
    def age_last(self):
        if 5 <= int(str(self.age)[-1]) <= 9:
            return 'лет'
        elif 2 <= int(str(self.age)[-1]) <= 4:
            return 'года'
        else:
            return 'год'

    def __str__(self):
        return f"{self.user.username}"


class Address(models.Model):
    customer = models.ForeignKey('Customer', related_name="addresses", on_delete=models.CASCADE, verbose_name='Покупатель')
    city = models.CharField(max_length=50, verbose_name='Город')
    metro = models.CharField(max_length=50, blank=True, null=True, verbose_name='ст. Метро')
    street = models.CharField(max_length=300, verbose_name='Улица, дом, квартира, подъезд')
    building = models.CharField(max_length=7, verbose_name='Дом')
    apartment = models.CharField(max_length=5, blank=True, null=True, verbose_name='Квартира')
    entrance = models.CharField(max_length=2, blank=True, null=True, verbose_name='Подъезд')
    primary = models.BooleanField(default=True, verbose_name='Основной адрес?')

    class Meta:
        verbose_name = 'Адрес покупателя'
        verbose_name_plural = 'Адреса покупателей'

    def __str__(self):
        return f"Адрес пользователя {self.customer.user.username} | {self.city}, {self.metro}, {self.street}, {self.street}, {self.building}"


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













