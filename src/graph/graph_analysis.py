from graphframes import GraphFrame
from pyvis.network import Network
import os

def run_pagerank(graph: GraphFrame, max_iter: int = 10):
    print("\n📊 === PageRank ===")
    results = graph.pageRank(resetProbability=0.15, maxIter=max_iter)
    results.vertices.select("id", "pagerank").orderBy("pagerank", ascending=False).show(truncate=False)


def run_connected_components(graph: GraphFrame):
    print("\n🔗 === Componentes Conectados ===")
    components = graph.connectedComponents()
    components.select("id", "component").orderBy("component").show(truncate=False)


def run_bfs(graph: GraphFrame, from_expr: str, to_expr: str, max_path_length: int = 3):
    print(f"\n🔍 === BFS de {from_expr} até {to_expr} ===")
    path = graph.bfs(fromExpr=from_expr, toExpr=to_expr, maxPathLength=max_path_length)
    path.show(truncate=False)


def show_degrees(graph: GraphFrame):
    print("\n📈 === Grau dos Vértices ===")
    degrees = graph.degrees
    degrees.orderBy("degree", ascending=False).show(truncate=False)


def export_graph_html(graph: GraphFrame, output_path: str = "finance_graph.html"):
    
    print("\n🌐 A gerar visualização 3D do grafo...")

    net = Network(height="700px", width="100%", bgcolor="#222222", font_color="white", notebook=False)

    nodes = graph.vertices.select("id").toPandas()["id"].tolist()
    for node in nodes:
        label = node.split("_")[0] if "_" in node else node
        color = "#33ccff" if node.isupper() else "#ffcc00"
        net.add_node(node, label=label, color=color)

    edges = graph.edges.select("src", "dst").toPandas()
    for _, row in edges.iterrows():
        net.add_edge(row["src"], row["dst"])

    os.makedirs("outputs", exist_ok=True)
    final_path = os.path.join("outputs", output_path)
    net.show(final_path)

    print(f"✅ Visualização guardada em: {final_path}")