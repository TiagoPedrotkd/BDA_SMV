from pyspark.sql import DataFrame, Window
from pyspark.sql.functions import col, avg, round as spark_round, lag
from pyspark.sql.functions import when
from pyspark.sql.functions import to_date

class Transformations:

    @staticmethod
    def clean_nulls(df: DataFrame) -> DataFrame:
        
        return df.na.drop(subset=["Date", "Open", "High", "Low", "Close", "Volume"])

    @staticmethod
    def convert_date_column(df: DataFrame) -> DataFrame:
        
        return df.withColumn("Date", to_date(col("Date"), "yyyy-MM-dd"))

    @staticmethod
    def calculate_daily_average(df: DataFrame) -> DataFrame:
        
        return df.groupBy("Date").agg(
            spark_round(avg("Close"), 2).alias("avg_close")
        ).orderBy("Date")

    @staticmethod
    def add_moving_average(df: DataFrame, window_size: int = 3) -> DataFrame:

        window_spec = Window.orderBy("Date").rowsBetween(-(window_size - 1), 0)
        return df.withColumn(
            f"ma_{window_size}", spark_round(avg("Close").over(window_spec), 2)
        )

    @staticmethod
    def calculate_percentage_return(df: DataFrame) -> DataFrame:
        
        window_spec = Window.orderBy("Date")
        return df.withColumn(
            "return_pct",
            spark_round((col("Close") - lag("Close", 1).over(window_spec)) / lag("Close", 1).over(window_spec) * 100, 2)
        )

    @staticmethod
    def fill_missing_with_zero(df: DataFrame, columns: list) -> DataFrame:

        for col_name in columns:
            df = df.withColumn(col_name, when(col(col_name).isNull(), 0).otherwise(col(col_name)))
        return df
    
    @staticmethod
    def add_market_cap(df: DataFrame) -> DataFrame:
    
        return df.withColumn(
            "Market_Cap_NVDA",
            spark_round(col("Close_NVDA") * col("Shares_Out_NVDA"), 2)
        )
    
    @staticmethod
    def add_pe_ratios(df: DataFrame) -> DataFrame:
        
        return df \
            .withColumn(
                "Trailing_PE_NVDA",
                spark_round(col("Close_NVDA") / col("EPS_TTM_NVDA"), 2)
            ) \
            .withColumn(
                "Forward_PE_NVDA",
                spark_round(col("Close_NVDA") / col("Forward_EPS_NVDA"), 2)
            )
    
    @staticmethod
    def add_ps_ratio(df: DataFrame) -> DataFrame:
        
        return df.withColumn(
            "PS_Ratio_NVDA",
            spark_round(col("Market_Cap_NVDA") / col("Total_Revenue_NVDA"), 2)
        )
    
    @staticmethod
    def add_enterprise_value(df: DataFrame) -> DataFrame:
        
        return df.withColumn(
            "EV_NVDA",
            spark_round(
                col("Market_Cap_NVDA") + col("Total_Debt_NVDA") - col("Cash_Equivalents_NVDA"),
                2
            )
        )
    
    def apply_all_financial_metrics(df: DataFrame) -> DataFrame:
       
        df = Transformations.add_market_cap(df)
        df = Transformations.add_pe_ratios(df)
        df = Transformations.add_ps_ratio(df)
        df = Transformations.add_enterprise_value(df)
        
        return df