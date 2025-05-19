import os
from datetime import datetime

class StreamConfig:
    
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    
    DATA_DIR = os.path.join(PROJECT_ROOT, "data")
    STREAM_INPUT_DIR = os.path.join(DATA_DIR, "streaming")
    EXTERNAL_DATA_DIR = os.path.join(DATA_DIR, "external")
    INTERIM_DATA_DIR = os.path.join(DATA_DIR, "interim")

    REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")
    FIGURES_DIR = os.path.join(REPORTS_DIR, "figures")
    EXPORT_DIR = os.path.join(PROJECT_ROOT, "exports")

    DATA_SCHEMA = (
        "Date STRING, "
        "Open DOUBLE, "
        "High DOUBLE, "
        "Low DOUBLE, "
        "Close DOUBLE, "
        "Volume DOUBLE"
    )

    SPARK_APP_NAME = "NVIDIA Structured Streaming"

    EXPORT_FORMATS = ["csv", "parquet"]
    EXPORT_PREFIX = "nvidia_stream"
    EXPORT_WITH_TIMESTAMP = True

    LOGGING_ENABLED = True
    DEBUG_MODE = True
    ENABLE_GRAPHFRAMES = True
    SPARK_LOG_LEVEL = "WARN"

    @staticmethod
    def g_timestamp():

        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    @classmethod
    def g_exp_path(cls, format : str) -> str:

        if format not in cls.EXPORT_FORMATS:
            raise ValueError(f"Invalid Format: {format}")
        
        filename = f"{cls.EXPORT_PREFIX}_{cls.get_timestamp()}.{format}"
        return os.path.join(cls.EXPORT_DIR, filename)