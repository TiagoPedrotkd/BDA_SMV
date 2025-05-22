from src.api.api_ingestor_graph import run_all

if __name__ == "__main__":
    symbols = ["NVDA", "INTC", "AMD"]
    run_all(symbols)
