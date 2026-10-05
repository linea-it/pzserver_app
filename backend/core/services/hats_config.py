"""Policies for exposing and rebuilding release HATS configurations."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from copy import deepcopy
from dataclasses import dataclass


logger = logging.getLogger(__name__)


PROTECTED_SECTION_NAMES = frozenset({"cluster", "dask", "executor"})
PROTECTED_FIELD_NAMES = frozenset(
    {
        "base_path",
        "catalog_folder",
        "catalog_path",
        "catalog_pattern",
        "directory",
        "folder",
        "path",
        "path_to_dustmaps",
        "which_release",
    }
)
PROTECTED_FIELD_PREFIXES = ("path_to_",)
PROTECTED_FIELD_SUFFIXES = ("_dir", "_directory", "_folder", "_path")


class HatsConfigPolicyError(ValueError):
    """Raised when a HATS configuration violates the public editing policy."""


@dataclass(frozen=True)
class HatsConfigHydrationResult:
    """Effective configuration and non-blocking policy warnings."""

    config: dict
    warnings: tuple[str, ...]


def sanitize_for_frontend(full_config):
    """Return a copy of a HATS config without infrastructure-controlled fields."""
    _require_mapping(full_config, "full_config")
    return _sanitize_node(full_config)


def hydrate_for_execution(editable_config, default_config):
    """Apply public edits while preserving protected values from the default."""
    _require_mapping(editable_config, "editable_config")
    _require_mapping(default_config, "default_config")

    warnings = []
    protected_paths = find_protected_paths(editable_config)
    if protected_paths:
        _add_warning(
            warnings,
            "Ignoring protected HATS configuration fields: "
            f"{', '.join(protected_paths)}.",
        )

    public_edits = sanitize_for_frontend(editable_config)
    hydrated_config = _overlay_public_values(
        default_config,
        public_edits,
        warnings=warnings,
    )
    return HatsConfigHydrationResult(
        config=hydrated_config,
        warnings=tuple(warnings),
    )


def find_protected_paths(config):
    """Return sorted dotted paths for protected fields present in a config."""
    _require_mapping(config, "config")
    return sorted(_find_protected_paths(config))


def is_protected_field(field_name):
    """Return whether a field name is reserved for infrastructure configuration."""
    if not isinstance(field_name, str):
        return False

    normalized_name = field_name.casefold()
    return (
        normalized_name in PROTECTED_SECTION_NAMES
        or normalized_name in PROTECTED_FIELD_NAMES
        or normalized_name.startswith(PROTECTED_FIELD_PREFIXES)
        or normalized_name.endswith(PROTECTED_FIELD_SUFFIXES)
    )


def _require_mapping(value, name):
    if not isinstance(value, Mapping):
        raise HatsConfigPolicyError(f"{name} must be an object.")


def _sanitize_node(value):
    if isinstance(value, Mapping):
        return {
            key: _sanitize_node(child)
            for key, child in value.items()
            if not is_protected_field(key)
        }
    if isinstance(value, list):
        return [_sanitize_node(item) for item in value]
    return deepcopy(value)


def _find_protected_paths(value, path=()):
    protected_paths = []

    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = (*path, key)
            if is_protected_field(key):
                protected_paths.append(_format_path(child_path))
                continue
            protected_paths.extend(_find_protected_paths(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            protected_paths.extend(_find_protected_paths(child, (*path, index)))

    return protected_paths


def _contains_protected_fields(value):
    if isinstance(value, Mapping):
        return any(
            is_protected_field(key) or _contains_protected_fields(child)
            for key, child in value.items()
        )
    if isinstance(value, list):
        return any(_contains_protected_fields(child) for child in value)
    return False


def _overlay_public_values(default_value, editable_value, path=(), warnings=None):
    if warnings is None:
        warnings = []

    if isinstance(default_value, Mapping) and isinstance(editable_value, Mapping):
        result = deepcopy(default_value)
        for key, child in editable_value.items():
            child_path = (*path, key)
            if key in default_value:
                result[key] = _overlay_public_values(
                    default_value[key],
                    child,
                    child_path,
                    warnings,
                )
            else:
                result[key] = deepcopy(child)
        return result

    if isinstance(default_value, list) and isinstance(editable_value, list):
        if not _contains_protected_fields(default_value):
            return deepcopy(editable_value)

        if len(default_value) != len(editable_value):
            _add_warning(
                warnings,
                "Ignoring edit to HATS configuration list "
                f"'{_format_path(path)}' because it contains protected fields "
                "and its length was changed.",
            )
            return deepcopy(default_value)

        return [
            _overlay_public_values(
                default_child,
                editable_child,
                (*path, index),
                warnings,
            )
            for index, (default_child, editable_child) in enumerate(
                zip(default_value, editable_value)
            )
        ]

    if _contains_protected_fields(default_value):
        _add_warning(
            warnings,
            "Ignoring edit to HATS configuration field "
            f"'{_format_path(path)}' because it would replace an object "
            "containing protected fields.",
        )
        return deepcopy(default_value)

    return deepcopy(editable_value)


def _add_warning(warnings, message):
    warnings.append(message)
    logger.warning(message)


def _format_path(path):
    formatted = ""
    for part in path:
        if isinstance(part, int):
            formatted += f"[{part}]"
        else:
            formatted += f".{part}" if formatted else str(part)
    return formatted or "<root>"
