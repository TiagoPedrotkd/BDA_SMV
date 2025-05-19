from pyspark.sql import SparkSession
from src.config_stream import StreamConfig

class SparkInitializer:

    _spark_instance = None

    @classmethod
    def g_spark(cls) -> SparkSession:

        if cls._spark_instance is None:
            builder = SparkSession.builder \
                .appName(StreamConfig.SPARK_APP_NAME) \
                .master("local[*]") \
                .config("spark.sql.shuffle.partitions", "4") \
                .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
                .config("spark.sql.legacy.timeParserPolicy", "LEGACY") \
                .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
                .config("spark.sql.files.ignoreCorruptFiles", "true") \
                .config("spark.sql.sources.partitionOverwriteMode", "dynamic") \
                .config("spark.ui.showConsoleProgress", "false")

            if StreamConfig.ENABLE_GRAPHFRAMES:
                builder = builder.config("spark.jars.packages", "graphframes:graphframes:0.8.2-spark3.1-s_2.12")

            cls._spark_instance = builder.getOrCreate()

            cls._set_logging_level(cls._spark_instance, StreamConfig.SPARK_LOG_LEVEL)

            if StreamConfig.DEBUG_MODE:
                print(f"✅ SparkSession initialize with app: {StreamConfig.SPARK_APP_NAME}")

        return cls._spark_instance
    
    @staticmethod
    def _set_logging_level(spark: SparkSession, level: str = "WARN"):
        spark.sparkContext.setLogLevel(level.upper())