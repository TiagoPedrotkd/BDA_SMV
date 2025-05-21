import os
import time
from pyspark.sql import DataFrame
from src.streaming.spark_session import SparkInitializer
from src.streaming.transformations import Transformations
from src.utils.stream_utils import StreamUtils
from src.config_stream import StreamConfig


class StreamProcessor:

    def __init__(self):
        self.spark = SparkInitializer.g_spark()
        self.utils = StreamUtils(base_dir=StreamConfig.EXPORT_DIR)
        self.input_dir = os.path.abspath(StreamConfig.STREAM_INPUT_DIR)
        self.processed_files = set()

    def read_batch_file(self, filepath: str) -> DataFrame:
        df = self.spark.read.option("header", True).schema(StreamConfig.DATA_SCHEMA).csv(filepath)
        return df

    def apply_transformations(self, df: DataFrame) -> DataFrame:
        df = Transformations.clean_nulls(df)
        df = Transformations.convert_date_column(df)
        return df

    def run(self):
        print("🔁 Simulador de Streaming iniciado (modo local sem winutils)...")
        print(f"📂 Pasta monitorizada: {self.input_dir}")

        while True:
            files = [f for f in os.listdir(self.input_dir) if f.endswith(".csv")]
            new_files = [f for f in files if f not in self.processed_files]

            for filename in new_files:
                full_path = os.path.join(self.input_dir, filename)
                print(f"\n📥 Novo ficheiro encontrado: {filename}")

                try:
                    df = self.read_batch_file(full_path)
                    df_transformed = self.apply_transformations(df)

                    df_transformed.show(10, truncate=False)

                    self.processed_files.add(filename)
                except Exception as e:
                    print(f"❌ Erro ao processar {filename}: {e}")

            time.sleep(5)
