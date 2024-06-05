import importlib
import importlib.util
import json
import logging
import pathlib
import sys

import yaml
from django.conf import settings
from django.db.models import Q

logger = logging.getLogger()


def get_pipelines():
    sys_pipes_file = pathlib.Path(settings.PIPELINES_DIR, 'pipelines.yaml')
    with open(sys_pipes_file, encoding="utf-8") as _file:
        return yaml.safe_load(_file)


def get_pipeline(name):
    system_pipelines = get_pipelines()
    pipeline = system_pipelines.get(name, None)
    assert pipeline, f"Pipeline {name} not found."
    pipeline['name'] = name
    return pipeline


def load_config(schema_path, config={}):
    mod = load_module_from_file(schema_path)
    return mod.Config(**config)


def import_module(module):
    return importlib.import_module(module)


def load_module_from_file(module):
    spec = importlib.util.spec_from_file_location(f"{module}.mod", module)
    assert spec, f"No module named '{module}'."
    mod = importlib.util.module_from_spec(spec)
    assert mod, f"Failed to import python module: {module}"
    sys.modules[f"{module}.mod"] = mod
    spec.loader.exec_module(mod)
    return mod


def load_executor(executor):
    assert validate_executor(executor), f"No executor named '{executor}'."
    mod = import_module(f"core.executors.{executor}")
    return getattr(mod, f"Executor{executor.capitalize()}")


def validate_executor(executor):
    try: import_module(f"core.executors.{executor}")
    except ModuleNotFoundError: return False
    return True


def validate_json(data):
    try: json.loads(data)
    except ValueError: return False
    return True


def validate_config(config):
    if not config: return True
    return validate_json(config) and isinstance(json.loads(config), dict)


def get_returncode(process_dir):
    try:
        with open(f"{process_dir}/return.code", encoding="utf-8") as _file:
            content = _file.readline()
            return int(content.replace('\n',''))
    except Exception as err:
        logger.error(f"Error when redeeming return code: {err}")
        return -1
    

def format_query_to_char(key, value, fields):
    condition = Q.OR if key.endswith("__or") else Q.AND
    values = value.split(",")
    query = Q()

    for value in values:
        subfilter = Q()
        for field in fields:
            subfilter.add(Q(**{f"{field}__icontains": value}), Q.OR)

        query.add(subfilter, condition)

    return query