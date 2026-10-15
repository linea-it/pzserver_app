from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0060_alter_productfile_size_and_n_rows"),
    ]

    operations = [
        migrations.RenameField(
            model_name="release",
            old_name="has_mag_hats",
            new_name="can_convert_flux_to_mag",
        ),
        migrations.AlterField(
            model_name="release",
            name="can_convert_flux_to_mag",
            field=models.BooleanField(
                default=False,
                help_text=(
                    "Flux is the default. Enable this option to allow users to "
                    "convert flux measurements to magnitudes."
                ),
                verbose_name="Allow flux-to-magnitude conversion",
            ),
        ),
        migrations.RemoveField(
            model_name="release",
            name="has_flux_hats",
        ),
    ]
