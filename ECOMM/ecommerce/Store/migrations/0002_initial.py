# Generated by Django 5.1.4 on 2025-01-18 00:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Store', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='mystore',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='order',
            name='buyer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders_as_buyer', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='order',
            name='seller',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders_as_seller', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='orderdetails',
            name='name',
            field=models.ForeignKey(max_length=35, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='product',
            name='store',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Store.mystore'),
        ),
        migrations.AddField(
            model_name='cart',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Store.product'),
        ),
        migrations.AddField(
            model_name='reviews',
            name='order',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='Store.order'),
        ),
        migrations.AddField(
            model_name='wishlist',
            name='name',
            field=models.OneToOneField(max_length=30, on_delete=django.db.models.deletion.CASCADE, to='Store.product'),
        ),
    ]
