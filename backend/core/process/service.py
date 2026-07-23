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
        self.maestro = None

    def _set_submission_stage(self, stage):
        self.process._submission_stage = stage
        return stage

    def _get_maestro(self):
        if self.maestro is None:
            self.maestro = Maestro(url=settings.ORCHEST_URL)
        return self.maestro

    def submit(self):
        request_data = getattr(self.request, "data", {}) or {}
        request_keys = sorted(request_data.keys()) if hasattr(request_data, "keys") else []
        stage = self._set_submission_stage("start")

        LOGGER.info(
            "Submitting process to orchestration process_id=%s pipeline=%s upload_id=%s upload_path=%s release_id=%s request_keys=%s",
            self.process.pk,
            self.process.pipeline.name,
            self.process.upload_id,
            self.process.upload.path,
            self.process.release_id,
            request_keys,
        )

        try:
            stage = self._set_submission_stage("init_maestro")
            maestro = self._get_maestro()

            stage = self._set_submission_stage("resolve_handler")
            handler_cls = BasePipelineHandler.get_handler(self.process.pipeline.name)
            LOGGER.debug(
                "Resolved pipeline handler process_id=%s pipeline=%s handler=%s",
                self.process.pk,
                self.process.pipeline.name,
                handler_cls.__name__,
            )

            stage = self._set_submission_stage("build_config")
            handler = handler_cls(self.request, self.process)
            used_config = handler.build_config()

            stage = self._set_submission_stage("build_inputs")
            inputs = InputsBuilder(self.process).build()

            used_config.setdefault("inputs", {})
            used_config["inputs"]["specz"] = inputs

            output_format = self.request.data.get("output_format")

            if output_format and output_format != "specz":
                used_config["output_format"] = output_format

            used_config["output_dir"] = str(self.process.upload.path)
            used_config["output_root_dir"] = settings.UPLOAD_DIR

            LOGGER.debug(
                "Prepared process config process_id=%s pipeline=%s stage=%s input_count=%s config_keys=%s output_dir=%s output_root_dir=%s output_format=%s",
                self.process.pk,
                self.process.pipeline.name,
                stage,
                len(inputs),
                sorted(used_config.keys()),
                used_config.get("output_dir"),
                used_config.get("output_root_dir"),
                used_config.get("output_format", "specz"),
            )

            stage = self._set_submission_stage("start_orchestration")
            orch_process = maestro.start(
                pipeline=self.process.pipeline.name,
                config=used_config,
            )

            self.process.orchestration_process_id = orch_process.get("id")
            self.process.path = orch_process.get("path_str")
            orch_used_config = orch_process.get("used_config", {})
            if isinstance(orch_used_config, str):
                orch_used_config = json.loads(orch_used_config or "{}")
            self.process.used_config = orch_used_config

            stage = self._set_submission_stage("save_process")
            self.process.save()
            LOGGER.info(
                "Orchestration accepted process submission process_id=%s orchestration_process_id=%s process_path=%s pipeline=%s",
                self.process.pk,
                self.process.orchestration_process_id,
                self.process.path,
                self.process.pipeline.name,
            )
        except Exception:
            LOGGER.exception(
                "Process submission stage failed process_id=%s pipeline=%s stage=%s upload_id=%s upload_path=%s release_id=%s request_keys=%s",
                self.process.pk,
                self.process.pipeline.name,
                stage,
                self.process.upload_id,
                self.process.upload.path,
                self.process.release_id,
                request_keys,
            )
            raise

    def stop(self):
        orchestration_process_id = self.process.orchestration_process_id

        if not orchestration_process_id:
            raise ValueError(
                f"Process[{self.process.pk}]: orchestration process not found."
            )

        maestro = self._get_maestro()
        maestro.stop(orchestration_process_id)
        status_data = maestro.status(orchestration_process_id)
        self.process.status = status_data.get("status", "Stopping*")
        self.process.save()

        return self.process
