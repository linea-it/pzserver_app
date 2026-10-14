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
            "metadata": {"release": "lsst_dp1"},
            "input": {
                "catalog_path": "/datasets/lsst_dp1",
                "catalog_pattern": "objects-*.parquet",
                "ra_col": "coord_ra",
                "dec_col": "coord_dec",
            },
            "photometry": {
                "measurements": [
                    {
                        "name": "cModel",
                        "input": {"type": "flux"},
                        "output": {"type": "mag_dered"},
                    }
                ]
            },
            "output": {
                "base_path": "/processes/science_catalogs",
                "save_as": "parquet",
            },
            "dust": {
                "path_to_dustmaps": "/datasets/dustmaps",
                "use_dustmap": "sfd",
            },
            "collection": {"margin": {"threshold_arcsec": 10.0}},
            "execution": {
                "executor": "slurm",
                "slurm": {"queue": "cpu_pipelines"},
            },
        }

    def test_sanitize_removes_infrastructure_fields(self):
        sanitized = sanitize_for_frontend(self.default_config)

        self.assertNotIn("execution", sanitized)
        self.assertEqual({}, sanitized["metadata"])
        self.assertNotIn("catalog_path", sanitized["input"])
        self.assertNotIn("catalog_pattern", sanitized["input"])
        self.assertNotIn("base_path", sanitized["output"])
        self.assertNotIn("path_to_dustmaps", sanitized["dust"])
        self.assertEqual("coord_ra", sanitized["input"]["ra_col"])
        self.assertEqual(
            "mag_dered",
            sanitized["photometry"]["measurements"][0]["output"]["type"],
        )
        self.assertEqual("sfd", sanitized["dust"]["use_dustmap"])

    def test_sanitize_removes_nested_path_fields_and_execution_sections(self):
        config = {
            "items": [
                {
                    "name": "catalog",
                    "staging_directory": "/tmp/staging",
                }
            ],
            "runtime": {
                "execution": {"executor": "local"},
                "value": 42,
            },
        }

        sanitized = sanitize_for_frontend(config)

        self.assertEqual({"name": "catalog"}, sanitized["items"][0])
        self.assertEqual({"value": 42}, sanitized["runtime"])

    def test_sanitize_protects_canonical_science_catalogs_infrastructure(self):
        config = {
            "metadata": {"release": "lsst_dp1"},
            "input": {
                "catalog_path": "/datasets/dp1",
                "ra_col": "coord_ra",
            },
            "photometry": {
                "measurements": [
                    {
                        "name": "cModel",
                        "output": {"type": "mag_dered"},
                    }
                ]
            },
            "output": {
                "save_as": "parquet",
                "base_path": "/processes/science_catalogs",
            },
            "execution": {
                "executor": "local",
                "local": {"n_workers": 3},
            },
        }

        sanitized = sanitize_for_frontend(config)

        self.assertEqual({}, sanitized["metadata"])
        self.assertNotIn("catalog_path", sanitized["input"])
        self.assertEqual("coord_ra", sanitized["input"]["ra_col"])
        self.assertNotIn("base_path", sanitized["output"])
        self.assertNotIn("execution", sanitized)
        self.assertEqual(
            "mag_dered",
            sanitized["photometry"]["measurements"][0]["output"]["type"],
        )

        sanitized["photometry"]["measurements"][0]["output"]["type"] = (
            "flux"
        )
        hydrated = hydrate_for_execution(sanitized, config).config

        self.assertEqual("lsst_dp1", hydrated["metadata"]["release"])
        self.assertEqual("/datasets/dp1", hydrated["input"]["catalog_path"])
        self.assertEqual(config["execution"], hydrated["execution"])
        self.assertEqual(
            "flux",
            hydrated["photometry"]["measurements"][0]["output"]["type"],
        )

    def test_sanitize_does_not_mutate_source(self):
        original = deepcopy(self.default_config)

        sanitize_for_frontend(self.default_config)

        self.assertEqual(original, self.default_config)

    def test_hydrate_applies_public_edits_and_restores_protected_values(self):
        editable = sanitize_for_frontend(self.default_config)
        editable["photometry"]["measurements"][0]["output"]["type"] = "flux"
        editable["dust"]["use_dustmap"] = "planck"
        editable["collection"]["margin"]["threshold_arcsec"] = 15.0

        result = hydrate_for_execution(editable, self.default_config)
        hydrated = result.config

        self.assertEqual((), result.warnings)
        self.assertEqual(
            "flux",
            hydrated["photometry"]["measurements"][0]["output"]["type"],
        )
        self.assertEqual("planck", hydrated["dust"]["use_dustmap"])
        self.assertEqual(
            15.0,
            hydrated["collection"]["margin"]["threshold_arcsec"],
        )
        self.assertEqual(
            "/datasets/lsst_dp1",
            hydrated["input"]["catalog_path"],
        )
        self.assertEqual(
            "/datasets/dustmaps",
            hydrated["dust"]["path_to_dustmaps"],
        )
        self.assertEqual("slurm", hydrated["execution"]["executor"])

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
            hydrated["input"]["catalog_path"],
        )
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
            "collection": {"margin": {"threshold_arcsec": 10.0}},
        }
        editable = {
            "sources": [],
            "collection": {"margin": {"threshold_arcsec": 20.0}},
        }

        with self.assertLogs("core.services.hats_config", level="WARNING") as logs:
            result = hydrate_for_execution(editable, default_config)
        hydrated = result.config

        self.assertIn("list 'sources'", logs.output[0])
        self.assertIn("list 'sources'", result.warnings[0])
        self.assertEqual(default_config["sources"], hydrated["sources"])
        self.assertEqual(
            20.0,
            hydrated["collection"]["margin"]["threshold_arcsec"],
        )

    def test_find_protected_paths_returns_nested_paths(self):
        config = {
            "execution": {"executor": "local"},
            "input": {"catalog_path": "/datasets/catalog"},
            "sources": [{"cache_dir": "/tmp/cache"}],
        }

        self.assertEqual(
            ["execution", "input.catalog_path", "sources[0].cache_dir"],
            find_protected_paths(config),
        )

    def test_policy_requires_object_roots(self):
        with self.assertRaisesRegex(HatsConfigPolicyError, "must be an object"):
            sanitize_for_frontend([])

        with self.assertRaisesRegex(HatsConfigPolicyError, "must be an object"):
            hydrate_for_execution({}, [])
