# Generated by Django 4.0.2 on 2023-03-15 17:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_release_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='survey',
        ),
    ]
