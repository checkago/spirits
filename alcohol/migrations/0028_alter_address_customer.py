# Generated by Django 3.2.8 on 2021-11-20 09:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('alcohol', '0027_auto_20211119_1907'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='customer', to='alcohol.customer', verbose_name='Покупатель'),
        ),
    ]
