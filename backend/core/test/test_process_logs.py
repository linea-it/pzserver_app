import tempfile
from pathlib import Path

from core.utils import get_logs
from django.test import SimpleTestCase, override_settings


class GetLogsTestCase(SimpleTestCase):
    def test_returns_empty_logs_when_paths_are_missing(self):
        logs = get_logs(None, None)

        self.assertEqual("", logs["pipeline"]["content"])
        self.assertEqual("", logs["slurm"]["content"])

    def test_reads_logs_from_product_dir_when_process_dir_is_missing(self):
        with tempfile.TemporaryDirectory() as upload_root:
            product_relpath = "validation_results/sample-product"
            pipeline_log = (
                Path(upload_root) / product_relpath / "process_info" / "pipeline.log"
            )
            pipeline_log.parent.mkdir(parents=True, exist_ok=True)
            pipeline_log.write_text("pipeline output", encoding="utf-8")

            with override_settings(UPLOAD_DIR=upload_root):
                logs = get_logs(None, product_relpath)

            self.assertEqual("pipeline output", logs["pipeline"]["content"])
            self.assertEqual("", logs["slurm"]["content"])
