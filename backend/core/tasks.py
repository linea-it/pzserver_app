import logging
import pathlib

from celery import shared_task
from core.maestro import Maestro
from core.models import Process
from core.models.product_file import FileRoles
from core.product_steps import RegistryProduct
from core.utils import get_ucd_columns, load_yaml
from django.conf import settings
from django.utils import dateparse, timezone

LOGGER = logging.getLogger()


@shared_task()
def check_processes():
    """Checks the processing status in Orchestration and update the PZ Server
    database with processing information.

    Returns:
        bool: True, if an update was made. False, if no update was made.
    """

    monitoring_statuses = ["Stopping", "Pending", "Running", "Queued"]
    LOGGER.debug(f"Monitoring the following statuses: {monitoring_statuses}")

    processes = Process.objects.filter(status__in=monitoring_statuses)

    if not processes:
        return False

    maestro = Maestro(settings.ORCHEST_URL)

    for process in processes:
        LOGGER.debug(f"Consulting the {process} process status.")
        process_orch_id = process.orchestration_process_id  # type: ignore

        if not process_orch_id:
            message = f"Process {str(process.pk)} without Orchestration ID."
            LOGGER.error(message)
            process = update_process_info(process, "Failed", {})
            continue

        process_orch = maestro.status(process_orch_id)
        process_orch_status = process_orch.get("status")  # type: ignore

        LOGGER.debug(f"-> Process orchestration ID: {process_orch_id}")
        LOGGER.debug(f"-> Status: {process_orch_status}")

        if process_orch_status == "Running" and process.status == "Pending":
            started_at = process_orch.get("started_at", str(process.created_at))
            process.started_at = dateparse.parse_datetime(started_at)
            process.status = process_orch_status
            process.save()

        if process_orch_status == "Successful":
            register_outputs(process.pk)
        elif process_orch_status == "Failed":
            process.upload.status = 9  # Failed status
            process.upload.save()

        if process_orch_status != process.status:
            process = update_process_info(
                process=process,
                process_orch_status=process_orch_status,
                data=process_orch,
            )
            LOGGER.debug(f"{process} has been updated (new status: {process.status})")

    return True


def update_process_info(process, process_orch_status, data):
    """Updates basic process information

    Args:
        process (Process): process object
        process_orch_status (str): process orchestration status
        data (dict): process info

    Returns:
        Process: process object
    """
    started_at = data.get("started_at", str(process.created_at))
    ended_at = data.get("ended_at", str(timezone.now()))

    if not ended_at:
        ended_at = str(timezone.now())

    process.started_at = dateparse.parse_datetime(started_at)
    process.ended_at = dateparse.parse_datetime(ended_at)
    process.status = process_orch_status
    process.save()
    return process


def register_outputs(process_id):
    """Records the outputs in the database

    Args:
        process_id (int): process ID
    """

    LOGGER.info(f"[process {process_id}]: starting upload registration...")

    file_roles = dict(FileRoles.choices)
    file_roles = {str(v).lower(): k for k, v in file_roles.items()}

    process = Process.objects.get(pk=process_id)
    process_dir = pathlib.Path(settings.PROCESSING_DIR, process.path)
    process_file = process_dir.joinpath("process.yml")

    LOGGER.debug(f"[process {process_id}]: info filepath {process_file}")

    reg_product = RegistryProduct(process.upload.pk)

    process_file_dict = load_yaml(process_file)
    outputs = process_file_dict.get("outputs", None)

    try:
        for output in outputs:
            LOGGER.debug("-> output: %s", output)
            root_dir = output.get("root_dir")
            relative_path = output.get("path")
            filepath = pathlib.Path(root_dir, relative_path).resolve()
            rolename = output.get("role")
            columns_assoc = output.get("columns_assoc", None)

            if columns_assoc:
                _columns = associate_columns(columns_assoc)
                LOGGER.debug(f"Columns mapping: {_columns}")
                reg_product.create_product_contents(_columns)

            role_id = file_roles.get(rolename, file_roles.get("description"))
            reg_product.create_product_file(filepath, relative_path, role_id)
            process.upload.save()

        reg_product.registry()
        process.upload.status = 1  # Published status
        process.upload.save()
        process.save()
        LOGGER.info(f"[process {process_id}]: registration completed!")
    except Exception as _:
        process.upload.status = 9  # Failed status
        process.upload.save()
        process.save()
        LOGGER.error(f"[process {process_id}]: Failed to upload register!")


def associate_columns(columns_map):
    """Associate columns

    Args:
        columns_map (dict): columns mapping
    """

    columns = {}
    columns_required = ["ra", "dec", "z"]
    ucd_columns = get_ucd_columns()

    for key, value in columns_map.items():
        columns[value] = ucd_columns.get(key, {})
        if key in columns_required:
            columns_required.remove(key)

    if columns_required:
        message = f"The column(s) was not filled: {','.join(columns_required)}"
        raise ValueError(message)

    return columns
