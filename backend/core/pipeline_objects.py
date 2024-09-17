from pathlib import Path

from core.utils import get_pipeline, get_pipelines
from pydantic import BaseModel, validator


class Pipeline():
    def __init__(self):
        self.__raw_pipelines = get_pipelines()

    def all(self):
        pipelines = []
        for pipename, data in self.__raw_pipelines.items():
            data["name"] = pipename
            pipelines.append(PipelineModel(**data))
        return pipelines
    
    def get(self, name):
        data = self.__raw_pipelines.get("name", {})
        data["name"] = name
        return PipelineModel(**data)


class PipelineModel(BaseModel):
    name: str
    path: str
    executor: str
    runner: str
    executable: str
    version: str
    display_name: str | None
    schema_config: str | None

    @validator('path', pre=True)
    def validate_path(cls, value):
        assert Path(value).is_dir(), f"Folder '{value}' not found."
        return value
    
    @validator('schema_config', pre=True)
    def validate_config(cls, value):
        assert Path(value).is_file(), f"File '{value}' not found."
        return value


if __name__ == "__main__":
    from core.utils import get_pipeline
    pipe_info = get_pipeline('cross_lsdb')
    pipeline = Pipeline(**pipe_info)