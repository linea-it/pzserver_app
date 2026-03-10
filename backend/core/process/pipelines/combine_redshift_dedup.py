import pathlib

from core.process.pipelines.base import BasePipelineHandler
from django.conf import settings
import logging

LOGGER = logging.getLogger("django")


class CombineRedshiftHandler(BasePipelineHandler):
    pipeline_name = "combine_redshift_dedup"

    def build_config(self):
        used_config = self.process.used_config or {}

        uploaded_flags = self.request.FILES.get("flags_translation_file")

        if uploaded_flags:
            LOGGER.debug("Received uploaded flags_translation_file: %s", uploaded_flags.name)
            upload_base = pathlib.Path(
                settings.UPLOAD_DIR,
                self.process.upload.path,
            )

            upload_base.mkdir(parents=True, exist_ok=True)

            filepath = upload_base / uploaded_flags.name

            with open(filepath, "wb+") as f:
                for chunk in uploaded_flags.chunks():
                    f.write(chunk)

            used_config.setdefault("param", {})
            used_config["param"]["flags_translation_file"] = str(filepath)
        else:
            LOGGER.debug("No flags_translation_file uploaded")

        return used_config
