import pathlib
from collections.abc import Mapping

from core.maestro import Maestro
from core.process.pipelines.base import BasePipelineHandler
from core.services.hats_config import HatsConfigPolicyError, hydrate_for_execution
from django.conf import settings


class TrainingSetMakerHandler(BasePipelineHandler):
    pipeline_name = "training_set_maker"

    def build_config(self):
        used_config = self.process.used_config or {}

        self._hydrate_hats_config(used_config)

        if self.process.release:
            release_path = pathlib.Path(
                settings.DATASETS_DIR,
                self.process.release.name,
            )

            used_config.setdefault("inputs", {})

            # The release root is used to resolve relative infrastructure paths
            # in param.hats_config before science_catalogs runs.
            used_config["inputs"]["dataset"] = {
                "path": str(release_path),
                "columns": {"id": self.process.release.indexing_column},
            }

        return used_config

    def _hydrate_hats_config(self, used_config):
        param = used_config.get("param")
        if not isinstance(param, Mapping) or "hats_config" not in param:
            return

        if not self.process.release:
            raise HatsConfigPolicyError(
                "A release is required when param.hats_config is provided."
            )

        default_response = Maestro(url=settings.ORCHEST_URL).hats_config(
            self.process.release.name
        )
        if not isinstance(default_response, Mapping):
            raise HatsConfigPolicyError(
                "Orchestration returned an invalid HATS configuration response."
            )

        result = hydrate_for_execution(
            editable_config=param["hats_config"],
            default_config=default_response.get("config"),
        )
        param["hats_config"] = result.config
