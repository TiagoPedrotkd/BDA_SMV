import os
import pandas as pd
import networkx as nx
from pyvis.network import Network


def load_all_company_data(folder_path: str):
    datasets = []
    for file in os.listdir(folder_path):
        if file.endswith(".csv"):
            company = file.split("_")[0].upper()
            df = pd.read_csv(os.path.join(folder_path, file))
            datasets.append((company, df))
    return datasets


def build_graph(folder_path: str, output_html: str = "outputs/finance_graph_simulated.html"):
    os.makedirs("outputs", exist_ok=True)

    G = nx.DiGraph()
    net = Network(height="700px", width="100%", bgcolor="#222", font_color="white")

    datasets = load_all_company_data(folder_path)

    for company, df in datasets:
        G.add_node(company, label=company, color="#00bfff")
        indicators = [
            col for col in df.columns if col not in [
                "Date", "Time", "open", "high", "low", "close", "volume", "datetime"
            ]
        ]
        for ind in indicators:
            G.add_node(ind, label=ind, color="#ffcc00")
            avg_value = df[ind].mean()
            G.add_edge(company, ind, value=avg_value)

    for node, attr in G.nodes(data=True):
        net.add_node(node, label=attr.get("label", node), color=attr.get("color", "#dddddd"))

    for src, dst, attr in G.edges(data=True):
        net.add_edge(src, dst, title=f"valor médio: {attr['value']:.2f}")

    try:
        net.show(output_html)
    except AttributeError as e:
        print("⚠️ PyVis falhou ao gerar HTML (problema conhecido com template). A tentar fallback...")
        net.write_html(output_html)

    print(f"✅ Grafo exportado para HTML: {output_html}")
