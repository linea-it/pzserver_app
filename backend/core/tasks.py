import logging
import pathlib
import shutil

from celery import shared_task
from core.maestro import Maestro
from core.models import Process
from core.models.product_file import FileRoles
from core.product_steps import RegistryProduct
from core.utils import load_yaml
from django.conf import settings
from django.utils import dateparse, timezone

logger = logging.getLogger()


@shared_task()
def check_processes():
    """ Checks the processing status in Orchestration and update the PZ Server
    database with processing information.

    Returns:
        bool: True, if an update was made. False, if no update was made.
    """
    
    monitoring_statuses = ["Stopping", "Pending", "Running"]
    logger.info(f"Monitoring the following statuses: {monitoring_statuses}")

    processes = Process.objects.filter(status__in=monitoring_statuses)

    if not processes:
        return False
    
    maestro = Maestro(settings.ORCHEST_URL)
    
    for process in processes:
        logger.info(f"Consulting the {process} process status.")
        process_orch_id = process.orchestration_process_id  # type: ignore

        if not process_orch_id:
            message = f"Process {str(process.pk)} without Orchestration ID."
            logger.error(message)
            process = update_process_info(process, "Failed", {})
            continue

        process_orch = maestro.status(process_orch_id)
        process_orch_status = process_orch.get("status")  # type: ignore

        logger.debug(f"-> Process orchestration ID: {process_orch_id}")
        logger.debug(f"-> Status: {process_orch_status}")

        if process_orch_status == "Running" and process.status == "Pending":
            started_at = process_orch.get("started_at", str(process.created_at))
            process.started_at = dateparse.parse_datetime(started_at)
            process.status = process_orch_status
            process.save()

        if process_orch_status == "Successful":
            register_outputs(process.pk)
            
        if process_orch_status != process.status:
            process = update_process_info(
                process=process,
                process_orch_status=process_orch_status,
                data=process_orch
            )
            logger.info(
                f"{process} has been updated (new status: {process.status})"
            )

    
    return True


def update_process_info(process, process_orch_status, data):
    """ Updates basic process information

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
    """ Records the outputs in the database

    Args:
        process_id (int): process ID
    """

    logger.info(f"[process {process_id}]: starting upload registration...")

    file_roles = dict(FileRoles.choices)
    file_roles = {str(v).lower(): k for k, v in file_roles.items()}

    process = Process.objects.get(pk=process_id)
    process_dir = pathlib.Path(settings.PROCESSING_DIR, process.path)
    process_file = process_dir.joinpath("process.yml")

    logger.debug(f"[process {process_id}]: info filepath {process_file}")

    reg_product = RegistryProduct(process.upload.pk)

    process_file_dict = load_yaml(process_file)
    outputs = process_file_dict.get("outputs", None)

    try:
        for output in outputs:
            logger.debug("-> output: %s", output)
            filepath = output.get("path")
            rolename = output.get("role")
            role_id = file_roles.get(rolename, file_roles.get("description"))
            upload_path = copy_upload(filepath, process.upload.path)
            reg_product.create_product_file(upload_path, role_id)
            process.upload.save()

        reg_product.registry()
        process.upload.status = 1  # Published status
        process.upload.save()
        process.save()
        logger.info(f"[process {process_id}]: registration completed!")
    except Exception as _:
        process.upload.status = 9  # Failed status
        process.upload.save()
        process.save()
        logger.exception(f"[process {process_id}]: Failed to upload register!")


def copy_upload(filepath, upload_dir):
    filepath = pathlib.Path(filepath)
    new_filepath = pathlib.Path(settings.MEDIA_ROOT, upload_dir, filepath.name)
    shutil.copyfile(str(filepath), str(new_filepath))
    return str(new_filepath)


if __name__ == "__main__":
    register_outputs(5)
