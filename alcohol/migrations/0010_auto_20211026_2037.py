# Generated by Django 3.2.8 on 2021-10-26 17:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('alcohol', '0009_auto_20211025_2115'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartproduct',
            name='product',
        ),
        migrations.RemoveField(
            model_name='product',
            name='category',
        ),
        migrations.AddField(
            model_name='cartproduct',
            name='content_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cartproduct',
            name='object_id',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='cart',
            name='final_price',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=9, null=True, verbose_name='Общая стоимость'),
        ),
        migrations.AlterField(
            model_name='cart',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='alcohol.customer', verbose_name='Покупатель'),
        ),
        migrations.AlterField(
            model_name='cart',
            name='products',
            field=models.ManyToManyField(blank=True, related_name='related_cart', to='alcohol.CartProduct', verbose_name='Товары в корзине'),
        ),
        migrations.AlterField(
            model_name='cart',
            name='total_products',
            field=models.IntegerField(default=0, verbose_name='Общее кол-во товаров в корзине'),
        ),
        migrations.AlterField(
            model_name='cartproduct',
            name='cart',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='alcohol.cart', verbose_name='Корзина'),
        ),
        migrations.AlterField(
            model_name='cartproduct',
            name='final_price',
            field=models.DecimalField(decimal_places=2, max_digits=9, verbose_name='Общая стоимость'),
        ),
        migrations.AlterField(
            model_name='cartproduct',
            name='qty',
            field=models.PositiveIntegerField(default=1, verbose_name='Количество'),
        ),
    ]
