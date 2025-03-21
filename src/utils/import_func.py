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
    
def enrich_nvidia_data(df, ticker="NVDA", printing = False):

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])
        df.set_index("Date", inplace=True)
    df = df[~df.index.duplicated(keep="last")]  # Remove duplicates

    nvda = yf.Ticker(ticker)
    info = nvda.info
    balance_sheet = nvda.balance_sheet

    try:
        # ✅ Market Cap Calculation (Daily Basis)
        outstanding_shares = nvda.get_shares_full(start=df.index.min(), end=df.index.max())
        if outstanding_shares is not None and not outstanding_shares.empty:
            outstanding_shares_df = pd.DataFrame(
                {"Shares_Out_NVDA": outstanding_shares.values}, 
                index=pd.to_datetime(outstanding_shares.index).tz_localize(None)
            )
            outstanding_shares_df = outstanding_shares_df[~outstanding_shares_df.index.duplicated(keep="last")]
            outstanding_shares_df = outstanding_shares_df.resample("D").ffill()
            df = df.merge(outstanding_shares_df, left_index=True, right_index=True, how="left")
            df["Market_Cap_NVDA"] = df["Close_NVDA"] * df["Shares_Out_NVDA"]
        else:
            df["Shares_Out_NVDA"] = None
            df["Market_Cap_NVDA"] = None

        # ✅ Trailing & Forward P/E Ratios
        trailing_eps = info.get("trailingEps", None)
        forward_eps = info.get("forwardEps", None)
        df["Trailing_PE_NVDA"] = df["Close_NVDA"] / trailing_eps if trailing_eps else None
        df["Forward_PE_NVDA"] = df["Close_NVDA"] / forward_eps if forward_eps else None

        # ✅ Price-to-Sales (P/S) Ratio
        total_revenue = info.get("totalRevenue", None)
        df["Total_Revenue_NVDA"] = total_revenue if total_revenue else None
        df["PS_Ratio_NVDA"] = df["Market_Cap_NVDA"] / total_revenue if total_revenue else None

        # ✅ Debt & Cash (Quarterly Data → Resampled to Daily)
        try:
            total_debt = balance_sheet.loc["Total Debt"].dropna()
            cash_equivalents = balance_sheet.loc["Cash And Cash Equivalents"].dropna()
            debt_cash_df = pd.DataFrame(
                {"Total_Debt_NVDA": total_debt, "Cash_Equivalents_NVDA": cash_equivalents}
            )
            debt_cash_df.index = pd.to_datetime(debt_cash_df.index).tz_localize(None)
            debt_cash_df = debt_cash_df[~debt_cash_df.index.duplicated(keep="last")]
            debt_cash_df = debt_cash_df.resample("D").ffill()
            df = df.merge(debt_cash_df, left_index=True, right_index=True, how="left")
        except KeyError:
            df["Total_Debt_NVDA"] = None
            df["Cash_Equivalents_NVDA"] = None

        # ✅ Handling Missing Values
        df["TD_CE_Missing_NVDA"] = df[["Total_Debt_NVDA", "Cash_Equivalents_NVDA"]].isna().any(axis=1).astype(int)
        df["Shares_Out_Missing_NVDA"] = df["Shares_Out_NVDA"].isna().astype(int)
        df["PE_Missing_NVDA"] = df[["Trailing_PE_NVDA", "Forward_PE_NVDA"]].isna().any(axis=1).astype(int)
        df["PS_Missing_NVDA"] = df["PS_Ratio_NVDA"].isna().astype(int)

        # ✅ Replacing missing financial values with 0 (only for calculations)
        df["Total_Debt_NVDA"] = df["Total_Debt_NVDA"].fillna(0).astype(float)
        df["Cash_Equivalents_NVDA"] = df["Cash_Equivalents_NVDA"].fillna(0).astype(float)

        # ✅ Enterprise Value Calculation with Missing Values Handling
        df["EV_NVDA"] = df.apply(
            lambda row: (
                None if row["TD_CE_Missing_NVDA"] == 1
                else row["Market_Cap_NVDA"] + row["Total_Debt_NVDA"] - row["Cash_Equivalents_NVDA"]
            ), axis=1
        )
        if printing:
            print("✅ Data Enrichment Successful! Sample Data:\n", df.head())

        return df

    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return df
    

def enrich_intel_data(df, ticker="INTC", printing = False):

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])
        df.set_index("Date", inplace=True)
    df = df[~df.index.duplicated(keep="last")]

    nvda = yf.Ticker(ticker)
    info = nvda.info
    balance_sheet = nvda.balance_sheet

    try:
        # ✅ Market Cap Calculation (Daily Basis)
        outstanding_shares = nvda.get_shares_full(start=df.index.min(), end=df.index.max())
        if outstanding_shares is not None and not outstanding_shares.empty:
            outstanding_shares_df = pd.DataFrame(
                {"Shares_Out_INTC": outstanding_shares.values}, 
                index=pd.to_datetime(outstanding_shares.index).tz_localize(None)
            )
            outstanding_shares_df = outstanding_shares_df[~outstanding_shares_df.index.duplicated(keep="last")]
            outstanding_shares_df = outstanding_shares_df.resample("D").ffill()
            df = df.merge(outstanding_shares_df, left_index=True, right_index=True, how="left")
            df["Market_Cap_INTC"] = df["Close_INTC"] * df["Shares_Out_INTC"]
        else:
            df["Shares_Out_INTC"] = None
            df["Market_Cap_INTC"] = None

        # ✅ Trailing & Forward P/E Ratios
        trailing_eps = info.get("trailingEps", None)
        forward_eps = info.get("forwardEps", None)
        df["Trailing_PE_INTC"] = df["Close_INTC"] / trailing_eps if trailing_eps else None
        df["Forward_PE_INTC"] = df["Close_INTC"] / forward_eps if forward_eps else None

        # ✅ Price-to-Sales (P/S) Ratio
        total_revenue = info.get("totalRevenue", None)
        df["Total_Revenue_INTC"] = total_revenue if total_revenue else None
        df["PS_Ratio_INTC"] = df["Market_Cap_INTC"] / total_revenue if total_revenue else None

        # ✅ Debt & Cash (Quarterly Data → Resampled to Daily)
        try:
            total_debt = balance_sheet.loc["Total Debt"].dropna()
            cash_equivalents = balance_sheet.loc["Cash And Cash Equivalents"].dropna()
            debt_cash_df = pd.DataFrame(
                {"Total_Debt_INTC": total_debt, "Cash_Equivalents_INTC": cash_equivalents}
            )
            debt_cash_df.index = pd.to_datetime(debt_cash_df.index).tz_localize(None)
            debt_cash_df = debt_cash_df[~debt_cash_df.index.duplicated(keep="last")]
            debt_cash_df = debt_cash_df.resample("D").ffill()
            df = df.merge(debt_cash_df, left_index=True, right_index=True, how="left")
        except KeyError:
            df["Total_Debt_INTC"] = None
            df["Cash_Equivalents_INTC"] = None

        # ✅ Handling Missing Values
        df["TD_CE_Missing_INTC"] = df[["Total_Debt_INTC", "Cash_Equivalents_INTC"]].isna().any(axis=1).astype(int)
        df["Shares_Out_Missing_INTC"] = df["Shares_Out_INTC"].isna().astype(int)
        df["PE_Missing_INTC"] = df[["Trailing_PE_INTC", "Forward_PE_INTC"]].isna().any(axis=1).astype(int)
        df["PS_Missing_INTC"] = df["PS_Ratio_INTC"].isna().astype(int)

        # ✅ Replacing missing financial values with 0 (only for calculations)
        df["Total_Debt_INTC"] = df["Total_Debt_INTC"].fillna(0).astype(float)
        df["Cash_Equivalents_INTC"] = df["Cash_Equivalents_INTC"].fillna(0).astype(float)

        # ✅ Enterprise Value Calculation with Missing Values Handling
        df["EV_INTC"] = df.apply(
            lambda row: (
                None if row["TD_CE_Missing_INTC"] == 1
                else row["Market_Cap_INTC"] + row["Total_Debt_INTC"] - row["Cash_Equivalents_INTC"]
            ), axis=1
        )
        if printing:
            print("✅ Data Enrichment Successful! Sample Data:\n", df.head())

        return df

    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return df
    

def enrich_amd_data(df, ticker="AMD", printing = False):

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])
        df.set_index("Date", inplace=True)
    df = df[~df.index.duplicated(keep="last")]

    nvda = yf.Ticker(ticker)
    info = nvda.info
    balance_sheet = nvda.balance_sheet

    try:
        # ✅ Market Cap Calculation (Daily Basis)
        outstanding_shares = nvda.get_shares_full(start=df.index.min(), end=df.index.max())
        if outstanding_shares is not None and not outstanding_shares.empty:
            outstanding_shares_df = pd.DataFrame(
                {"Shares_Out_AMD": outstanding_shares.values}, 
                index=pd.to_datetime(outstanding_shares.index).tz_localize(None)
            )
            outstanding_shares_df = outstanding_shares_df[~outstanding_shares_df.index.duplicated(keep="last")]
            outstanding_shares_df = outstanding_shares_df.resample("D").ffill()
            df = df.merge(outstanding_shares_df, left_index=True, right_index=True, how="left")
            df["Market_Cap_AMD"] = df["Close_AMD"] * df["Shares_Out_AMD"]
        else:
            df["Shares_Out_AMD"] = None
            df["Market_Cap_AMD"] = None

        # ✅ Trailing & Forward P/E Ratios
        trailing_eps = info.get("trailingEps", None)
        forward_eps = info.get("forwardEps", None)
        df["Trailing_PE_AMD"] = df["Close_AMD"] / trailing_eps if trailing_eps else None
        df["Forward_PE_AMD"] = df["Close_AMD"] / forward_eps if forward_eps else None

        # ✅ Price-to-Sales (P/S) Ratio
        total_revenue = info.get("totalRevenue", None)
        df["Total_Revenue_AMD"] = total_revenue if total_revenue else None
        df["PS_Ratio_AMD"] = df["Market_Cap_AMD"] / total_revenue if total_revenue else None

        # ✅ Debt & Cash (Quarterly Data → Resampled to Daily)
        try:
            total_debt = balance_sheet.loc["Total Debt"].dropna()
            cash_equivalents = balance_sheet.loc["Cash And Cash Equivalents"].dropna()
            debt_cash_df = pd.DataFrame(
                {"Total_Debt_AMD": total_debt, "Cash_Equivalents_AMD": cash_equivalents}
            )
            debt_cash_df.index = pd.to_datetime(debt_cash_df.index).tz_localize(None)
            debt_cash_df = debt_cash_df[~debt_cash_df.index.duplicated(keep="last")]
            debt_cash_df = debt_cash_df.resample("D").ffill()
            df = df.merge(debt_cash_df, left_index=True, right_index=True, how="left")
        except KeyError:
            df["Total_Debt_AMD"] = None
            df["Cash_Equivalents_AMD"] = None

        # ✅ Handling Missing Values
        df["TD_CE_Missing_AMD"] = df[["Total_Debt_AMD", "Cash_Equivalents_AMD"]].isna().any(axis=1).astype(int)
        df["Shares_Out_Missing_AMD"] = df["Shares_Out_AMD"].isna().astype(int)
        df["PE_Missing_AMD"] = df[["Trailing_PE_AMD", "Forward_PE_AMD"]].isna().any(axis=1).astype(int)
        df["PS_Missing_AMD"] = df["PS_Ratio_AMD"].isna().astype(int)

        # ✅ Replacing missing financial values with 0 (only for calculations)
        df["Total_Debt_AMD"] = df["Total_Debt_AMD"].fillna(0).astype(float)
        df["Cash_Equivalents_AMD"] = df["Cash_Equivalents_AMD"].fillna(0).astype(float)

        # ✅ Enterprise Value Calculation with Missing Values Handling
        df["EV_AMD"] = df.apply(
            lambda row: (
                None if row["TD_CE_Missing_AMD"] == 1
                else row["Market_Cap_AMD"] + row["Total_Debt_AMD"] - row["Cash_Equivalents_AMD"]
            ), axis=1
        )
        if printing:
            print("✅ Data Enrichment Successful! Sample Data:\n", df.head())

        return df

    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return df