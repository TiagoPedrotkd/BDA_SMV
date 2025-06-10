import yfinance as yf
import pandas as pd

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

# Download AMD stock price data
# amd_data = yf.download("AMD", start="2025-01-17", end="2025-05-09", interval="1d")

# Reset index to move date from index to a column
# amd_data.reset_index(inplace=True)

# Preview the data
# print(amd_data.head())

amd_data = pd.read_csv("amd_stock_data.csv")
print(amd_data.head())

amd_data = enrich_amd_data(amd_data)
amd_data.reset_index(inplace=True)
amd_data.to_csv("amd_stock_data_test.csv", index=False)
