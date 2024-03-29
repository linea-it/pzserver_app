# Generated by Django 4.0.2 on 2023-11-09 13:45

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0027_product_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='productfile',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='productfile',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
