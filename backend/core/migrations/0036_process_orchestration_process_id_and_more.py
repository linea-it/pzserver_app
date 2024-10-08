# Generated by Django 5.0.6 on 2024-06-25 20:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0035_remove_process_upload_product_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='process',
            name='orchestration_process_id',
            field=models.IntegerField(default=1000),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='process',
            name='status',
            field=models.CharField(default='Pending', max_length=255),
        ),
    ]
