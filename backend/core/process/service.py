import json

import core.process.pipelines

from core.maestro import Maestro
from core.process.builders.inputs_builder import InputsBuilder
from core.process.pipelines.base import BasePipelineHandler
from django.conf import settings
import logging

LOGGER = logging.getLogger("django")


class ProcessService:

    def __init__(self, request, process):
        self.request = request
        self.process = process
        self.maestro = Maestro(url=settings.ORCHEST_URL)

    def submit(self):
        handler_cls = BasePipelineHandler.get_handler(self.process.pipeline.name)
        handler = handler_cls(self.request, self.process)
        used_config = handler.build_config()

        inputs = InputsBuilder(self.process).build()

        used_config.setdefault("inputs", {})
        used_config["inputs"]["specz"] = inputs

        output_format = self.request.data.get("output_format")

        if output_format and output_format != "specz":
            used_config["output_format"] = output_format

        used_config["output_dir"] = str(self.process.upload.path)
        used_config["output_root_dir"] = settings.UPLOAD_DIR

        LOGGER.debug("Used config: %s", used_config)

        orch_process = self.maestro.start(
            pipeline=self.process.pipeline.name,
            config=used_config,
        )

        self.process.orchestration_process_id = orch_process.get("id")
        self.process.used_config = json.loads(orch_process.get("used_config", "{}"))
        self.process.path = orch_process.get("path_str")
        self.process.save()

    def stop(self):
        orchestration_process_id = self.process.orchestration_process_id

        if not orchestration_process_id:
            raise ValueError(
                f"Process[{self.process.pk}]: orchestration process not found."
            )

        self.maestro.stop(orchestration_process_id)
        status_data = self.maestro.status(orchestration_process_id)
        self.process.status = status_data.get("status", "Stopping*")
        self.process.save()

        return self.process
