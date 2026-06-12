import matplotlib.pyplot as plt
import networkx as nx
from typing import List, Dict
from qiskit_optimization.applications import Tsp

def plot_tsp_route(
    tsp_instance: Tsp,
    path: List[int],
    index_to_name: Dict[int, str],
    title: str = "TSP Optimized Route",
    save_path: str = None
):
    """
    Plots the TSP graph and highlights the optimized route.
    
    Args:
        tsp_instance: The TSP problem instance.
        path: List of node indices representing the solved path.
        index_to_name: Mapping from node index to display name.
        title: Title of the plot.
        save_path: Optional file path to save the plot image.
    """
    G = tsp_instance.graph
    
    # 1. Determine positions of nodes
    # Check if node coordinates exist (synthetic instances usually have them)
    has_pos = all('pos' in G.nodes[node] for node in G.nodes)
    if has_pos:
        pos = {node: G.nodes[node]['pos'] for node in G.nodes}
    else:
        # Fallback to circular layout if coordinates are not available (e.g. custom CSV)
        pos = nx.circular_layout(G)
        
    plt.figure(figsize=(8, 8))
    
    # 2. Draw all nodes
    nx.draw_networkx_nodes(G, pos, node_color='#64B5F6', node_size=600, edgecolors='#1976D2')
    
    # 3. Draw node labels with custom names
    labels = {i: index_to_name[i] for i in G.nodes}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=12, font_weight='bold')
    
    # 4. Draw all possible paths (edges) in light gray
    nx.draw_networkx_edges(G, pos, edgelist=G.edges(), edge_color='#E0E0E0', width=1.5, style='dashed')
    
    # 5. Create a directed graph for the solved route to show direction
    route_edges = []
    for i in range(len(path)):
        u = path[i]
        v = path[(i + 1) % len(path)]
        route_edges.append((u, v))
        
    route_di_graph = nx.DiGraph()
    route_di_graph.add_nodes_from(G.nodes)
    route_di_graph.add_edges_from(route_edges)
    
    # 6. Draw the optimized route edges in bold red with arrows
    nx.draw_networkx_edges(
        route_di_graph, 
        pos, 
        edgelist=route_edges, 
        edge_color='#E53935', 
        width=3.0, 
        arrows=True, 
        arrowstyle='-|>', 
        arrowsize=20,
        connectionstyle='arc3,rad=0.08'  # Curved arrows to prevent overlapping bidirectional lines
    )
    
    plt.title(title, fontsize=14, fontweight='bold')
    plt.axis('off')
    plt.tight_layout()
    
    # Save the plot if a path is specified
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved route visualization to: {save_path}")
        
    # Non-blocking show
    plt.show()
    plt.close()
