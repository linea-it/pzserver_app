from core.models.pipeline import Pipeline
from core.pipeline_objects import Pipeline as PipelineObject
from core.utils import load_module_from_file
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Synchronize pipelines from pipelines.xml into database"

    @transaction.atomic
    def handle(self, *args, **kwargs):

        pipelines_data = PipelineObject().all()

        for data in pipelines_data:
            try:
                system_config = (
                    load_module_from_file(data.schema_config).Config().model_dump()
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"Failed to load system config for {data.name}: {e}"
                    )
                )
                continue

            updated = Pipeline.objects.filter(name=data.name).update(
                display_name=data.display_name,
                version=data.version,
                system_config=system_config,
            )

            if updated:
                self.stdout.write(f"Updated: {data.name}")
            else:
                self.stdout.write(
                    self.style.WARNING(f"Pipeline not found: {data.name}")
                )

        self.stdout.write(self.style.SUCCESS("Pipelines synchronized successfully."))
