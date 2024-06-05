from pydantic import BaseModel
import os

DATASETS_DIR = os.getenv("DATASETS_DIR", "/datasets")


class Instance(BaseModel):
  processes: int = 1
  memory: str = "123GiB"
  queue: str = "cpu"
  job_extra_directives: list[str] = ["--propagate", "--time=2:00:00"]


class Adapt(BaseModel):
  maximum_jobs: int = 10


class LIneASlurm(BaseModel):
  instance: Instance = Instance()
  adapt: Adapt = Adapt()


class Local(BaseModel):
  n_workers: int = 2
  threads_per_worker: int = 2
  memory_limit: str = "1GiB"


class Inputs(BaseModel):
  photo: str = f"{DATASETS_DIR}/DatasetA"
  specz: str = f"{DATASETS_DIR}/DatasetB"


class Executor(BaseModel):
  local: Local = Local()
  linea_slurm: LIneASlurm = LIneASlurm()


class Config(BaseModel):
  output_dir: str = "./output"
  executor: Executor = Executor()
  inputs: Inputs = Inputs()


if __name__ == "__main__":
  import yaml

  cfg = Config()

  with open('config.yml', 'w') as outfile:
    yaml.dump(cfg.model_dump(), outfile)
