import requests
import pandas as pd
from datetime import datetime
import os
import time
from src.config_stream import StreamConfig


class APIIngestor:
    def __init__(self):
        self.symbol = "NVDA"
        self.api_key = "a7ba5d915f2e4ddd8a69a350b3c1a9b8"
        self.api_calls = 0
        self.call_reset_time = time.time()

    def wait_for_api_limit(self):
        if self.api_calls >= 7:
            elapsed = time.time() - self.call_reset_time
            if elapsed < 60:
                wait_time = 60 - elapsed
                print(f"⏳ A esperar {int(wait_time)}s para respeitar o limite de chamadas...")
                time.sleep(wait_time)
            self.api_calls = 0
            self.call_reset_time = time.time()

    def fetch_price_data(self, interval, from_date, to_date):
        self.wait_for_api_limit()
        try:
            url = "https://api.twelvedata.com/time_series"
            params = {
                "symbol": self.symbol,
                "interval": interval,
                "start_date": from_date,
                "end_date": to_date,
                "apikey": self.api_key,
                "format": "JSON",
                "outputsize": 5000
            }

            response = requests.get(url, params=params)
            self.api_calls += 1

            data = response.json()

            if "values" not in data:
                print(f"⚠️ Erro ao obter preços [{interval}]: {data.get('message', 'Resposta inválida')}")
                return pd.DataFrame()

            df = pd.DataFrame(data["values"])
            df["datetime"] = pd.to_datetime(df["datetime"])
            df = df.set_index("datetime").sort_index()

            cols = ["open", "high", "low", "close", "volume"]
            for col in cols:
                df[col] = pd.to_numeric(df[col], errors="coerce")

            return df

        except Exception as e:
            print(f"❌ Erro ao obter preços ({interval}): {e}")
            return pd.DataFrame()

    def fetch_technical_indicators(self, interval, from_date, to_date):
        base_url = "https://api.twelvedata.com"
        indicators = ["rsi", "sma", "ema", "macd", "stoch", "adx", "cci", "atr", "bbands"]
        dataframes = []

        for indicator in indicators:
            self.wait_for_api_limit()
            try:
                url = f"{base_url}/{indicator}"
                params = {
                    "symbol": self.symbol,
                    "interval": interval,
                    "start_date": from_date,
                    "end_date": to_date,
                    "apikey": self.api_key,
                    "format": "JSON"
                }

                response = requests.get(url, params=params)
                self.api_calls += 1

                if "application/json" in response.headers.get("Content-Type", ""):
                    data = response.json()
                else:
                    print(f"⚠️ {indicator}: resposta inválida (não JSON)")
                    continue

                if "values" not in data:
                    print(f"⚠️ Erro ao obter {indicator}: {data.get('message', 'Sem dados')}")
                    continue

                df = pd.DataFrame(data["values"])
                df["datetime"] = pd.to_datetime(df["datetime"])
                df = df.set_index("datetime").sort_index()
                df = df.add_prefix(f"{indicator.upper()}_")

                dataframes.append(df)

            except Exception as e:
                print(f"❌ Erro ao obter indicador {indicator}: {e}")
                continue

        if not dataframes:
            print("⚠️ Nenhum indicador técnico foi obtido.")
            return pd.DataFrame()

        return pd.concat(dataframes, axis=1)

    def save_to_csv(self, df: pd.DataFrame):
        if df.empty:
            print("⚠️ DataFrame final está vazio. Nada foi salvo.")
            return

        os.makedirs(StreamConfig.STREAM_INPUT_DIR, exist_ok=True)
        df = df.sort_index()

        date_str = datetime.now().strftime("%Y-%m-%d")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"nvda_full_{date_str}_{timestamp}.csv"
        path = os.path.join(StreamConfig.STREAM_INPUT_DIR, filename)

        df.reset_index(inplace=True)
        df["Date"] = df["datetime"].dt.strftime("%Y-%m-%d")
        df["Time"] = df["datetime"].dt.strftime("%H:%M")
        df.to_csv(path, index=False)
        print(f"📤 CSV completo guardado: {path}")

    def run(self):
        os.makedirs("data/cache", exist_ok=True)

        intervals = {
            "1min": 7,
            "5min": 30,
            "15min": 60,
            "1h": 730
        }

        today = datetime.now().date()
        cache_files = []

        for interval, days in intervals.items():
            from_date = (today - pd.Timedelta(days=days)).strftime("%Y-%m-%d")
            to_date = today.strftime("%Y-%m-%d")
            print(f"\n⏳ A recolher preços e indicadores técnicos ({interval}) desde {from_date} até {to_date}...")

            price_df = self.fetch_price_data(interval, from_date, to_date)
            tech_df = self.fetch_technical_indicators(interval, from_date, to_date)

            if price_df.empty:
                print("❌ Dados de preços não obtidos.")
                continue

            merged_df = price_df.join(tech_df, how="left")

            if merged_df.empty:
                print("❌ Dados finais estão vazios após junção.")
                continue

            merged_df = merged_df.sort_index()
            merged_df.reset_index(inplace=True)
            merged_df["Date"] = merged_df["datetime"].dt.strftime("%Y-%m-%d")
            merged_df["Time"] = merged_df["datetime"].dt.strftime("%H:%M")

            filename = f"nvda_{interval}_{to_date}.csv"
            cache_path = os.path.join("data/cache", filename)
            merged_df.to_csv(cache_path, index=False)
            print(f"📁 Cache salva: {cache_path}")
            cache_files.append(cache_path)

        if not cache_files:
            print("⚠️ Nenhum ficheiro foi salvo para consolidar.")
            return

        all_dfs = [pd.read_csv(f) for f in cache_files]
        combined_df = pd.concat(all_dfs, ignore_index=True)

        numeric_cols = combined_df.select_dtypes(include=["number"]).columns
        final_df = combined_df.groupby(["Date", "Time"], as_index=False)[numeric_cols].mean()

        cols = ["Date", "Time"] + [col for col in final_df.columns if col not in ["Date", "Time"]]
        final_df = final_df[cols]

        self.save_to_csv(final_df)