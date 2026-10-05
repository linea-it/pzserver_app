from copy import deepcopy

from core.services.hats_config import (
    HatsConfigPolicyError,
    find_protected_paths,
    hydrate_for_execution,
    sanitize_for_frontend,
)
from django.test import SimpleTestCase


class HatsConfigPolicyTestCase(SimpleTestCase):
    def setUp(self):
        self.default_config = {
            "executor": {
                "name": "slurm",
                "args": {"queue": "cpu_pipelines"},
            },
            "input": {
                "catalog_folder": "/datasets/lsst_dp1",
                "catalog_pattern": "objects-*.parquet",
                "which_release": "LSST_DP1",
                "input_col_model": "cModelFlux",
                "compute_magnitude": True,
                "compute_dereddening": True,
            },
            "output": {
                "base_path": "/processes/science_catalogs",
                "save_as": "hats",
                "col_final_pattern": "BAND_cModelMag_dered",
            },
            "dust": {
                "path_to_dustmaps": "/datasets/dustmaps",
                "use_dustmap": "sfd",
            },
            "collection": {"margin_threshold": 10.0},
        }

    def test_sanitize_removes_infrastructure_fields(self):
        sanitized = sanitize_for_frontend(self.default_config)

        self.assertNotIn("executor", sanitized)
        self.assertNotIn("catalog_folder", sanitized["input"])
        self.assertNotIn("catalog_pattern", sanitized["input"])
        self.assertNotIn("which_release", sanitized["input"])
        self.assertNotIn("base_path", sanitized["output"])
        self.assertNotIn("path_to_dustmaps", sanitized["dust"])
        self.assertEqual("cModelFlux", sanitized["input"]["input_col_model"])
        self.assertEqual("sfd", sanitized["dust"]["use_dustmap"])

    def test_sanitize_removes_nested_path_fields_and_cluster_sections(self):
        config = {
            "items": [
                {
                    "name": "catalog",
                    "staging_directory": "/tmp/staging",
                }
            ],
            "runtime": {
                "dask": {"scheduler": "tcp://scheduler:8786"},
                "value": 42,
            },
        }

        sanitized = sanitize_for_frontend(config)

        self.assertEqual({"name": "catalog"}, sanitized["items"][0])
        self.assertEqual({"value": 42}, sanitized["runtime"])

    def test_sanitize_does_not_mutate_source(self):
        original = deepcopy(self.default_config)

        sanitize_for_frontend(self.default_config)

        self.assertEqual(original, self.default_config)

    def test_hydrate_applies_public_edits_and_restores_protected_values(self):
        editable = sanitize_for_frontend(self.default_config)
        editable["input"]["compute_magnitude"] = False
        editable["dust"]["use_dustmap"] = "planck"
        editable["collection"]["margin_threshold"] = 15.0

        result = hydrate_for_execution(editable, self.default_config)
        hydrated = result.config

        self.assertEqual((), result.warnings)
        self.assertFalse(hydrated["input"]["compute_magnitude"])
        self.assertEqual("planck", hydrated["dust"]["use_dustmap"])
        self.assertEqual(15.0, hydrated["collection"]["margin_threshold"])
        self.assertEqual(
            "/datasets/lsst_dp1",
            hydrated["input"]["catalog_folder"],
        )
        self.assertEqual(
            "/datasets/dustmaps",
            hydrated["dust"]["path_to_dustmaps"],
        )
        self.assertEqual("slurm", hydrated["executor"]["name"])

    def test_hydrate_ignores_protected_fields_and_applies_other_edits(self):
        editable = sanitize_for_frontend(self.default_config)
        editable["input"]["catalog_path"] = "/etc/passwd"
        editable["scratch_directory"] = "/tmp/other"
        editable["dust"]["use_dustmap"] = "planck"

        with self.assertLogs("core.services.hats_config", level="WARNING") as logs:
            result = hydrate_for_execution(editable, self.default_config)
        hydrated = result.config

        self.assertIn("input.catalog_path, scratch_directory", logs.output[0])
        self.assertIn(
            "input.catalog_path, scratch_directory",
            result.warnings[0],
        )
        self.assertNotIn("scratch_directory", hydrated)
        self.assertEqual(
            "/datasets/lsst_dp1",
            hydrated["input"]["catalog_folder"],
        )
        self.assertNotIn("catalog_path", hydrated["input"])
        self.assertEqual("planck", hydrated["dust"]["use_dustmap"])

    def test_hydrate_ignores_replacing_parent_of_protected_fields(self):
        editable = sanitize_for_frontend(self.default_config)
        editable["input"] = "invalid"
        editable["dust"]["use_dustmap"] = "planck"

        with self.assertLogs("core.services.hats_config", level="WARNING") as logs:
            result = hydrate_for_execution(editable, self.default_config)
        hydrated = result.config

        self.assertIn("field 'input'", logs.output[0])
        self.assertIn("field 'input'", result.warnings[0])
        self.assertEqual(self.default_config["input"], hydrated["input"])
        self.assertEqual("planck", hydrated["dust"]["use_dustmap"])

    def test_hydrate_preserves_protected_fields_inside_lists(self):
        default_config = {
            "sources": [
                {
                    "catalog_path": "/datasets/source",
                    "label": "Default",
                }
            ]
        }
        editable = sanitize_for_frontend(default_config)
        editable["sources"][0]["label"] = "Edited"

        result = hydrate_for_execution(editable, default_config)
        hydrated = result.config

        self.assertEqual((), result.warnings)
        self.assertEqual("Edited", hydrated["sources"][0]["label"])
        self.assertEqual(
            "/datasets/source",
            hydrated["sources"][0]["catalog_path"],
        )

    def test_hydrate_ignores_resizing_list_with_protected_fields(self):
        default_config = {
            "sources": [
                {
                    "catalog_path": "/datasets/source",
                    "label": "Default",
                }
            ],
            "collection": {"margin_threshold": 10.0},
        }
        editable = {
            "sources": [],
            "collection": {"margin_threshold": 20.0},
        }

        with self.assertLogs("core.services.hats_config", level="WARNING") as logs:
            result = hydrate_for_execution(editable, default_config)
        hydrated = result.config

        self.assertIn("list 'sources'", logs.output[0])
        self.assertIn("list 'sources'", result.warnings[0])
        self.assertEqual(default_config["sources"], hydrated["sources"])
        self.assertEqual(20.0, hydrated["collection"]["margin_threshold"])

    def test_find_protected_paths_returns_nested_paths(self):
        config = {
            "cluster": {"workers": 2},
            "input": {"catalog_path": "/datasets/catalog"},
            "sources": [{"cache_dir": "/tmp/cache"}],
        }

        self.assertEqual(
            ["cluster", "input.catalog_path", "sources[0].cache_dir"],
            find_protected_paths(config),
        )

    def test_policy_requires_object_roots(self):
        with self.assertRaisesRegex(HatsConfigPolicyError, "must be an object"):
            sanitize_for_frontend([])

        with self.assertRaisesRegex(HatsConfigPolicyError, "must be an object"):
            hydrate_for_execution({}, [])
