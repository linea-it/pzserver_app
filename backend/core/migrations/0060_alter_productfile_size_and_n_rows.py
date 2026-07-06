from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0059_productfile_is_directory"),
    ]

    operations = [
        migrations.AlterField(
            model_name="productfile",
            name="n_rows",
            field=models.BigIntegerField(
                blank=True, null=True, verbose_name="Number of rows"
            ),
        ),
        migrations.AlterField(
            model_name="productfile",
            name="size",
            field=models.BigIntegerField(blank=True, null=True, verbose_name="Size"),
        ),
    ]
