# Generated by Django 5.0.6 on 2024-05-29 22:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0033_alter_process_upload'),
    ]

    operations = [
        migrations.AddField(
            model_name='process',
            name='upload_product_type',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, related_name='upload_product_type', to='core.producttype'),
            preserve_default=False,
        ),
    ]