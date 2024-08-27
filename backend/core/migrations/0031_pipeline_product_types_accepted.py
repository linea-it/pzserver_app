# Generated by Django 5.0.6 on 2024-05-29 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_process'),
    ]

    operations = [
        migrations.AddField(
            model_name='pipeline',
            name='product_types_accepted',
            field=models.ManyToManyField(related_name='pipelines', to='core.producttype'),
        ),
    ]