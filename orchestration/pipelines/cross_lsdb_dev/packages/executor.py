"""_summary_ """

from dask.distributed import LocalCluster
from dask_jobqueue import SLURMCluster
from utils import load_yml
import logging
from typing import Union


def get_executor_config(
    executor_key: str, config_file: str
) -> Union[LocalCluster, SLURMCluster]:
    """returns the configuration of where the pipeline will be run

    Args:
        executor_key (str): executor key
        config_file (str): config path

    Returns:
        Union[LocalCluster, SLURMCluster]: Executor object
    """

    logger = logging.getLogger()
    logger.info("Getting executor config: %s", executor_key)

    configs = load_yml(config_file)

    try:
        config = configs["executor"][executor_key]
    except KeyError:
        logger.warning("The executor key not found. Using minimal local config.")
        executor_key = "minimal"

    match executor_key:
        case "local":
            cluster = LocalCluster(**config)
        case "linea-slurm":
            icfg = config["instance"]
            cluster = SLURMCluster(**icfg)
            cluster.adapt(**config["adapt"])
        case _:
            cluster = LocalCluster(
                n_workers=1,
                threads_per_worker=1,
            )

    return cluster
