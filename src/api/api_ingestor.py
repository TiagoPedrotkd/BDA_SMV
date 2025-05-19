import requests
import pandas as pd
from datetime import datetime
import os
import time
import yfinance as yf

from src.config_stream import StreamConfig

class APIIngestor:
    def __init__(self):
        self.alpha_api_key = "demo"  # substitui pela tua chave
        self.symbol = "NVDA"
        self.interval = "1min"
        self.alpha_url = (
            f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&"
            f"symbol={self.symbol}&interval={self.interval}&apikey={self.alpha_api_key}&outputsize=compact"
        )
        self.last_timestamp_file = "last_saved_timestamp.txt"

    def fetch_intraday_data(self):
        response = requests.get(self.alpha_url)
        if response.status_code != 200:
            print("❌ ERROR API Alpha Vantage")
            return None

        raw = response.json().get("Time Series (1min)", {})
        if not raw:
            print("⚠️ Value not returned from Alpha Vantage")
            return None

        rows = []
        for timestamp, values in raw.items():
            row = {
                "Timestamp": timestamp,
                "Date": timestamp.split()[0],
                "Time": timestamp.split()[1],
                "Close_NVDA": float(values["4. close"])
            }
            rows.append(row)

        return pd.DataFrame(rows)

    def fetch_yahoo_fundamentals(self):
        info = yf.Ticker(self.symbol).info
        return {
            "Shares_Out_NVDA": info.get("sharesOutstanding"),
            "EPS_TTM_NVDA": info.get("trailingEps"),
            "Forward_EPS_NVDA": info.get("forwardEps"),
            "Total_Revenue_NVDA": info.get("totalRevenue"),
            "Total_Debt_NVDA": info.get("totalDebt"),
            "Cash_Equivalents_NVDA": info.get("totalCash")
        }

    def get_last_saved_timestamp(self):
        if os.path.exists(self.last_timestamp_file):
            with open(self.last_timestamp_file, "r") as f:
                return f.read().strip()
        return None

    def set_last_saved_timestamp(self, ts):
        with open(self.last_timestamp_file, "w") as f:
            f.write(ts)

    def merge_data(self, df: pd.DataFrame, fundamentals: dict) -> pd.DataFrame:
        if df is None or df.empty or fundamentals is None:
            return pd.DataFrame()

        last_saved = self.get_last_saved_timestamp()
        if last_saved:
            df = df[df["Timestamp"] > last_saved]

        if df.empty:
            print("⏹️ Nenhum novo dado para salvar.")
            return pd.DataFrame()

        for key, value in fundamentals.items():
            df[key] = value

        latest_ts = df["Timestamp"].max()
        self.set_last_saved_timestamp(latest_ts)

        return df.drop(columns=["Timestamp"])

    def save_to_csv(self, df: pd.DataFrame):
        if df.empty:
            return
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"nvda_{timestamp}.csv"
        path = os.path.join(StreamConfig.STREAM_INPUT_DIR, filename)
        df.to_csv(path, index=False)
        print(f"📤 CSV saved with data: {path}")

    def run(self, interval_seconds=60):
        while True:
            print("⏳ Obtaining Data...")
            df_intraday = self.fetch_intraday_data()
            fundamentals = self.fetch_yahoo_fundamentals()
            merged_df = self.merge_data(df_intraday, fundamentals)
            self.save_to_csv(merged_df)
            time.sleep(interval_seconds)