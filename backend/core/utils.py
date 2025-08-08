import glob
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


def get_lognames():
    """
    Returns a dictionary of names and their corresponding log names.
    """
    return {
        "pipeline": {"filename": ["pipeline.log", "*.log"]},
        "slurm": {"filename": ["run.out"]},
    }


def get_logs(process_dir, product_dir):
    """Returns a dictionary of log file paths for the given process or product directories.

    Args:
        process_dir (str): The directory where the process logs are stored.
        product_dir (str): The directory where the product logs are stored.
    Returns:
        dict: A dictionary containing log names and their content.
        If a log file is not found, its content will be an empty string.
    """

    logs = get_lognames()

    process_dir = pathlib.Path(settings.PROCESSING_DIR, process_dir)
    product_dir = pathlib.Path(settings.UPLOAD_DIR, product_dir)

    for _, data in logs.items():
        log = []
        lognames = data.get("filename", [])
        for fname in lognames:
            print(f"Searching for log file: {fname}")
            log = glob.glob(f"{process_dir}/**/{fname}", recursive=True)
            if not log:
                log = glob.glob(f"{product_dir}/**/{fname}", recursive=True)

            if log:
                break

        if log:
            with open(log[0], encoding="utf-8") as _file:
                data["content"] = _file.read()  # type: ignore
        else:
            data["content"] = ""  # type: ignore

    return logs


def get_ucd_columns():
    return {
        "id": {"alias": "ID", "ucd": "meta.id;meta.main"},
        "ra": {"alias": "RA", "ucd": "pos.eq.ra;meta.main"},
        "dec": {"alias": "Dec", "ucd": "pos.eq.dec;meta.main"},
        "z": {"alias": "z", "ucd": "src.redshift"},
        "z_err": {"alias": "z_err", "ucd": "stat.error;src.redshift"},
        "z_flag": {"alias": "z_flag", "ucd": "stat.rank"},
        "survey": {"alias": "survey", "ucd": "meta.curation"},
    }


def load_yaml(filepath, encoding="utf-8"):
    with open(filepath, encoding=encoding) as _file:
        return yaml.safe_load(_file)


def get_pipelines():
    sys_pipes_file = pathlib.Path(settings.PIPELINES_DIR, "pipelines.yaml")
    return load_yaml(sys_pipes_file)


def get_pipeline(name):
    system_pipelines = get_pipelines()
    pipeline = system_pipelines.get(name, None)
    assert pipeline, f"Pipeline {name} not found."
    pipeline["name"] = name
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
    try:
        import_module(f"core.executors.{executor}")
    except ModuleNotFoundError:
        return False
    return True


def validate_json(data):
    try:
        json.loads(data)
    except ValueError:
        return False
    return True


def validate_config(config):
    if not config:
        return True
    return validate_json(config) and isinstance(json.loads(config), dict)


def get_returncode(process_dir):
    try:
        with open(f"{process_dir}/return.code", encoding="utf-8") as _file:
            content = _file.readline()
            return int(content.replace("\n", ""))
    except Exception as err:
        logger.error(f"Error when redeeming return code: {err}")
        return -1


def format_query_to_char(key, value, fields) -> Q:
    condition = Q.OR if key.endswith("__or") else Q.AND
    values = value.split(",")
    query = Q()

    for value in values:
        subfilter = Q()
        for field in fields:
            subfilter.add(Q(**{f"{field}__icontains": value}), Q.OR)

        query.add(subfilter, condition)

    return query
