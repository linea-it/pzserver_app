from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0058_product_download_archive"),
    ]

    operations = [
        migrations.AddField(
            model_name="productfile",
            name="is_directory",
            field=models.BooleanField(default=False),
        ),
    ]
