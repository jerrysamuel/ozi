# Generated by Django 5.1.4 on 2025-01-19 15:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Store', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dispute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('buyer_email', models.EmailField(max_length=254)),
                ('seller_email', models.EmailField(max_length=254)),
                ('status', models.CharField(choices=[('OPEN', 'Open'), ('RESOLVED', 'Resolved')], default='OPEN', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='dispute', to='Store.order')),
            ],
        ),
    ]
