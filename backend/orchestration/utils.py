import json
import logging
import pathlib
from collections import namedtuple
from typing import Any, Dict, List, NamedTuple, Type, Union

import yaml
from django.conf import settings

PIPE_PATHFILE = pathlib.Path(settings.PIPELINES_DIR, settings.PIPELINES_FILE)

Json = Union[Dict[str, Any], List[Any], int, str, float, bool, Type[None]]


def read_yaml(yaml_file: str) -> Dict[str, Any]:
    with open(yaml_file, encoding="UTF-8") as _file:
        data = yaml.load(_file, Loader=yaml.loader.SafeLoader)
        return data


def dict_to_namedtuple(data: Dict[str, Any], label="Data") -> NamedTuple:
    _data = namedtuple(label, data)
    return _data(**data)


def dict_to_json(data: Dict[str, Any], indent: int = 4) -> Json:
    _data = json.dumps(data, indent=indent)
    return _data


def get_pipelines() -> Dict[str, Any]:
    if not PIPE_PATHFILE.is_file():
        raise FileNotFoundError(f"Pipeline list not found: {str(PIPE_PATHFILE)}")

    with open(PIPE_PATHFILE, encoding="UTF-8") as _file:
        pipelines = yaml.load(_file, Loader=yaml.loader.SafeLoader)
        return pipelines


def get_pipeline(name: str) -> Dict[str, Any]:
    pipelines = get_pipelines()
    pipeline = pipelines.get(name, None)
    if not pipeline:
        raise NotImplemented(f"Pipeline {name} not implemented")
    pipeline["basepath"] = pathlib.Path(settings.PIPELINES_DIR, name)
    return pipeline


def get_pipeline_config(pipeline_name: str) -> Dict[str, Any]:
    pipeline = get_pipeline(pipeline_name)
    filename = pipeline.get("config", "")
    basepath = pipeline.get("basepath", "")
    config_path = pathlib.Path(basepath, filename)
    if not config_path.is_file():
        raise NotImplemented(f"Pipeline {pipeline_name}: config not implemented")
    return read_yaml(str(config_path))


def merge_config(config_file: str, user_config: Dict[str, Any]) -> Dict[str, Any]:
    config = read_yaml(config_file)
    logging.debug("User config: %s", user_config)
    logging.debug("Default config: %s", config)
    config.update(user_config)
    logging.debug("Merge config: %s", config)

    return config


def get_pipeline_version(pipeline_name: str) -> str:
    pipeline = get_pipeline(pipeline_name)
    return pipeline.get("version", "")
