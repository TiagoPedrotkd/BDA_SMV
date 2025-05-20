from pyspark.sql import DataFrame
from src.streaming.spark_session import SparkInitializer
from src.streaming.transformations import Transformations
from src.utils.stream_utils import StreamUtils
from src.config_stream import StreamConfig

class StreamProcessor:
    
    def __init__(self):
        self.spark = SparkInitializer.g_spark()
        self.utils = StreamUtils(base_path=StreamConfig.EXPORT_DIR)

    def read_stream(self) -> DataFrame:
        return self.spark.readStream \
            .option("header", True) \
            .schema(StreamConfig.DATA_SCHEMA) \
            .csv(StreamConfig.STREAM_INPUT_DIR)

    def apply_transformations(self, df: DataFrame) -> DataFrame:
        df = Transformations.clean_nulls(df)
        df = Transformations.convert_date_column(df)
        df = Transformations.apply_all_financial_metrics(df)
        return df

    def run(self):
        df_stream = self.read_stream()
        df_transformed = self.apply_transformations(df_stream)

        query = df_transformed.writeStream \
            .format("csv") \
            .option("path", StreamConfig.EXPORT_DIR) \
            .option("checkpointLocation", "checkpoints/nvda_streaming_checkpoint/") \
            .outputMode("append") \
            .start()

        print("🚀 Spark Structured Streaming ativo. A processar ficheiros em tempo real...")
        query.awaitTermination()