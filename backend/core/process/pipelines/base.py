class BasePipelineHandler:
    registry = {}
    pipeline_name = None

    def __init_subclass__(cls, **kwargs):
        """
        Automatically register subclasses as pipeline handlers.
        """
        super().__init_subclass__(**kwargs)

        if cls.pipeline_name:
            BasePipelineHandler.registry[cls.pipeline_name] = cls

    def __init__(self, request, process):
        self.request = request
        self.process = process

    def build_config(self):
        raise NotImplementedError

    @classmethod
    def get_handler(cls, pipeline_name):
        if pipeline_name not in cls.registry:
            raise ValueError(
                f"Pipeline handler not registered: {pipeline_name}"
            )

        return cls.registry[pipeline_name]
