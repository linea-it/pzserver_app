# Generated by Django 4.0.2 on 2022-08-09 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_rename_roles_productfile_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='status',
            field=models.IntegerField(choices=[(0, 'Registering'), (1, 'Published'), (9, 'Failed')], default=0, verbose_name='Status'),
        ),
    ]
