# Generated by Django 5.0.6 on 2024-07-05 19:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0037_alter_process_orchestration_process_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="process",
            name="path",
            field=models.CharField(blank=True, default=None, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="release",
            name="name",
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
