# Generated by Django 4.0.2 on 2022-07-26 17:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_productcontent_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='description_file',
        ),
        migrations.RemoveField(
            model_name='product',
            name='main_file',
        ),
    ]
