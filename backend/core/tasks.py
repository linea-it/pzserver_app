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

logger = logging.getLogger("beat")


@shared_task()
def check_stopping():
    logger.info("Checking processes stopping...")

    procs_updated = []
    monitoring_statuses = ["Stopping"]
    procs_stopping = Process.objects.filter(status__in=monitoring_statuses)

    for proc in procs_stopping:
        logger.info(f"Consulting the {str(proc)} process status.")
        proc_orches_id = proc.orchestration_process_id  # type: ignore

        if not proc_orches_id:
            message = f"Process {str(proc.pk)} without Orchestration ID."
            logger.error(message)
            proc.status = "Failed"
            proc = update_dates(proc, {})
            proc.save()
            continue

        maestro = Maestro(settings.ORCHEST_URL)
        proc_orchest = maestro.status(proc_orches_id)
        proc_orchest_status = proc_orchest.get("status")  # type: ignore

        logger.info(f"-> Process orchestration ID: {proc_orches_id}")
        logger.info(f"-> Status: {proc_orchest_status}")

        if not proc_orchest_status in monitoring_statuses:
            proc.status = proc_orchest_status
            proc.save()
            logger.info(f"-> Process {str(proc)} updated.")
            procs_updated.append(proc_orches_id)

    return procs_updated


@shared_task()
def check_processes_finish():
    logger.info("Checking running processes...")

    procs_updated = []
    active_statuses = ["Pending", "Running"]
    procs_running = Process.objects.filter(status__in=active_statuses)

    for proc in procs_running:
        logger.info(f"Consulting the {str(proc)} process status.")
        proc_orches_id = proc.orchestration_process_id  # type: ignore

        if not proc_orches_id:
            message = f"Process {str(proc.pk)} without Orchestration ID."
            logger.error(message)
            proc.status = "Failed"
            proc = update_dates(proc, {})
            proc.save()
            continue

        maestro = Maestro(settings.ORCHEST_URL)
        proc_orchest = maestro.status(proc_orches_id)
        proc_orchest_status = proc_orchest.get("status")  # type: ignore

        logger.info(f"-> Process orchestration ID: {proc_orches_id}")
        logger.info(f"-> Status: {proc_orchest_status}")

        if proc_orchest_status == "Running" and proc.status == "Pending":
            started_at = proc_orchest.get("started_at", str(proc.created_at))
            proc.started_at = dateparse.parse_datetime(started_at)
            proc.status = proc_orchest_status
            proc.save()

        if not proc_orchest_status in active_statuses:
            proc.status = proc_orchest_status
            proc = update_dates(proc, proc_orchest)
            proc.save()
            register_outputs(proc.pk)
            logger.info(f"-> Process {str(proc)} updated.")
            procs_updated.append(proc_orches_id)

    return procs_updated


def update_dates(process, data):
    started_at = data.get("started_at", str(process.created_at))
    ended_at = data.get("ended_at", str(timezone.now()))
    process.started_at = dateparse.parse_datetime(started_at)
    process.ended_at = dateparse.parse_datetime(ended_at)
    return process


def register_outputs(process_id):
    """_summary_

    Args:
        process_id (_type_): _description_
    """

    file_roles = dict(FileRoles.choices)
    file_roles = {str(v).lower(): k for k, v in file_roles.items()}

    process = Process.objects.get(pk=process_id)
    process_dir = pathlib.Path(settings.PROCESSING_DIR, process.path)
    process_file = process_dir.joinpath("process.yml")

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
    except Exception as _:
        process.upload.status = 9  # Failed status
        process.upload.save()
        process.save()
        logger.exception("Failed to upload register!")


def copy_upload(filepath, upload_dir):
    filepath = pathlib.Path(filepath)
    new_filepath = pathlib.Path(settings.MEDIA_ROOT, upload_dir, filepath.name)
    logger.debug("new_filepath -> %s", str(new_filepath))
    shutil.copyfile(str(filepath), str(new_filepath))
    return str(new_filepath)


if __name__ == "__main__":
    register_outputs(5)
