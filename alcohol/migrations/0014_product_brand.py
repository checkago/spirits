# Generated by Django 3.2.8 on 2021-10-28 18:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('alcohol', '0013_remove_product_brand'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='brand',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='alcohol.brand', verbose_name='Бренд'),
            preserve_default=False,
        ),
    ]
