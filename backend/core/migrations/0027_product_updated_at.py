# Generated by Django 4.0.2 on 2023-11-09 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_productcontent_alias'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
