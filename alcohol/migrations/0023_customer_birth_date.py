# Generated by Django 3.2.8 on 2021-11-10 21:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alcohol', '0022_slider'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='birth_date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата рождения'),
        ),
    ]
