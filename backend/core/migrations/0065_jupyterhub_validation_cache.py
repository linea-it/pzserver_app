from django.core.management import call_command
from django.db import migrations


def create_cache(apps, schema_editor):
    call_command(
        "createcachetable",
        "jupyterhub_validation_cache",
        database=schema_editor.connection.alias,
        verbosity=0,
    )


def drop_cache(apps, schema_editor):
    schema_editor.execute(
        "DROP TABLE " + schema_editor.quote_name("jupyterhub_validation_cache")
    )


class Migration(migrations.Migration):
    dependencies = [("core", "0064_jupyterhubconsent")]
    operations = [migrations.RunPython(create_cache, drop_cache)]
