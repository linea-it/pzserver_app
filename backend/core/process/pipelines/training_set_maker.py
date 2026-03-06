import pathlib

from core.process.pipelines.base import BasePipelineHandler
from django.conf import settings


class TrainingSetMakerHandler(BasePipelineHandler):
    pipeline_name = "training_set_maker"

    def build_config(self):

        used_config = self.process.used_config or {}

        if self.process.release:
            release_path = pathlib.Path(
                settings.DATASETS_DIR,
                self.process.release.name,
            )

            used_config.setdefault("inputs", {})

            used_config["inputs"]["dataset"] = {
                "path": str(release_path),
                "columns": {"id": self.process.release.indexing_column},
            }

        return used_config
