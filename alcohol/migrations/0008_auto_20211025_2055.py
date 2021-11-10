# Generated by Django 3.2.8 on 2021-10-25 17:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('alcohol', '0007_alter_cart_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='final_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=9, verbose_name='Общая цена'),
        ),
        migrations.AlterField(
            model_name='cart',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='alcohol.customer', verbose_name='Владелец'),
        ),
        migrations.AlterField(
            model_name='cart',
            name='products',
            field=models.ManyToManyField(blank=True, related_name='related_cart', to='alcohol.CartProduct'),
        ),
        migrations.AlterField(
            model_name='cart',
            name='total_products',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
