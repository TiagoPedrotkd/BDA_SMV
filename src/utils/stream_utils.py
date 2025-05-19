import os
import shutil
from datetime import datetime
from pyspark.sql import DataFrame

class StreamUtils:

    def __init__(self, base_dir=""):
        self.base_dir = base_dir
        self._ensure_dir_exists(self.base_dir)

    def _log(self, message : str):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{now}] {message}")

    def _ensure_dir_exists(self, path: str):
        if not os.path.exists(path):
            os.makedirs(path)
            self._log(f"Folder created: {path}")
        else:
            self._log(f"Folder exists: {path}")

    def clear_directory(self, path : str = None):
        """
            Remove every file in the directory
        """

        target_path = path or self.base_dir
        if os.path.exists(target_path):
            shutil.rmtree(target_path)
            self._log(f"Folder Clean: {target_path}")
            os.makedirs(target_path)
        else:
            self._log(f"Folder not found to clean: {target_path}")

    
    def g_timestamped_path(self, prefix : str, extension : str = "") -> str:
        """
            Create a file name ou folder name with timestamp
        """

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = f"{prefix}_{timestamp}{extension}"

        return os.path.join(self.base_dir, name)
    
    def exp_to_csv(self, df : DataFrame, prefix="data"):

        path = self.g_timestamped_path(prefix=prefix)
        df.write.option("header", True).csv(path)
        self._log(f"✅ Export CSV to: {path}")

    def exp_to_parquet(self, df: DataFrame, prefix="data"):

        path = self.get_timestamped_path(prefix=prefix)
        df.write.mode("overwrite").parquet(path)
        self._log(f"✅ Export Parquet to: {path}")

    def export_to_json(self, df: DataFrame, prefix="data"):

        path = self.get_timestamped_path(prefix=prefix)
        df.write.mode("overwrite").json(path)
        self._log(f"✅ Export JSON to: {path}")

    def create_subfolder(self, name : str ) -> str:
        
        path = os.path.join(self.base_dir, name)
        self._ensure_dir_exists(path)
        return path
    
    def zip_exp(self, zip_name = "exports_backup.zip"):

        shutil.make_archive(zip_name.replace(".zip", ""), 'zip', self.base_dir)
        self._log(f"📦 Exported and Compacted to: {zip_name}")
