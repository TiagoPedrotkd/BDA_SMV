import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def init_import_data(ticker, interval, periods, printing=False):
    init_ticker = ticker
    init_interval = interval
    init_periods = periods
    init_delta = timedelta(days=90)

    dataframe = {}

    for period, (start_date, end_date) in init_periods.items():
        if printing:
            print(f"Baixando dados para {period} de {start_date.strftime('%Y-%m-%d')} a {end_date.strftime('%Y-%m-%d')}...")

        all_data = []
        current_date = start_date

        while current_date < end_date:
            next_date = min(current_date + init_delta, end_date)

            if printing:
                print(f"Baixando intervalo {current_date.strftime('%Y-%m-%d')} a {next_date.strftime('%Y-%m-%d')}...")
            
            data = yf.download(init_ticker, start=current_date.strftime('%Y-%m-%d'), 
                                end=next_date.strftime('%Y-%m-%d'), interval=init_interval)
            
            if not data.empty:
                data["Period"] = period
                all_data.append(data)
            
            current_date = next_date

        if all_data:
            dataframe[period] = pd.concat(all_data)
        else:
            print(f"⚠ Nenhum dado encontrado para {period}")

    df_all = pd.concat(dataframe.values(), ignore_index=False)

    return df_all
        