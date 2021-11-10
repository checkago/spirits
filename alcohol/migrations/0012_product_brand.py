# Generated by Django 3.2.8 on 2021-10-26 19:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('alcohol', '0011_auto_20211026_2040'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='brand',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='alcohol.brand', verbose_name='Бренд'),
            preserve_default=False,
        ),
    ]
