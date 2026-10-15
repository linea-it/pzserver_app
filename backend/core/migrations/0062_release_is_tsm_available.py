from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0061_replace_release_hats_flags"),
    ]

    operations = [
        migrations.AddField(
            model_name="release",
            name="is_tsm_available",
            field=models.BooleanField(
                default=True,
                help_text="Show this release in the Training Set Maker pipeline.",
                verbose_name="Available in Training Set Maker",
            ),
        ),
    ]
