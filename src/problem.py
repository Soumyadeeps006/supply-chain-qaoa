import pandas as pd
import numpy as np
import networkx as nx
from typing import Tuple, Dict
from qiskit_optimization.applications import Tsp

def generate_synthetic_problem(num_nodes: int) -> Tuple[Tsp, Dict[int, str]]:
    """
    Generates a synthetic TSP problem instance with random coordinates.
    
    Args:
        num_nodes: The number of locations (nodes) in the graph.
        
    Returns:
        A tuple of (Tsp instance, index_to_name mapping).
    """
    # Create a random TSP instance using Qiskit's helper
    tsp_instance = Tsp.create_random_instance(num_nodes, seed=123)
    
    # Create index to name mapping (e.g. 0 -> '0', 1 -> '1', etc.)
    index_to_name = {i: str(i) for i in range(num_nodes)}
    
    return tsp_instance, index_to_name

def load_custom_problem(csv_path: str) -> Tuple[Tsp, Dict[int, str]]:
    """
    Loads a custom distance matrix from a CSV file.
    The CSV must represent a square, symmetric matrix with node names as headers and row labels.
    
    Args:
        csv_path: Path to the CSV file.
        
    Returns:
        A tuple of (Tsp instance, index_to_name mapping).
    """
    # Load the CSV, using the first column as the index
    df = pd.read_csv(csv_path, index_col=0)
    
    # Check if the matrix is square
    if df.shape[0] != df.shape[1]:
        raise ValueError(
            f"Distance matrix must be square. Loaded shape: {df.shape}"
        )
    
    num_nodes = df.shape[0]
    node_names = list(df.columns)
    
    # Validate headers match row names
    row_names = list(df.index.astype(str))
    col_names = [str(c) for c in node_names]
    if col_names != row_names:
        # If they don't match exactly, at least verify they contain the same set
        if set(col_names) != set(row_names):
            raise ValueError("Row index names and column header names in the CSV do not match.")
    
    # Convert data to numeric
    matrix = df.to_numpy(dtype=float)
    
    # Check if the matrix is symmetric
    if not np.allclose(matrix, matrix.T, atol=1e-5):
        raise ValueError("Distance matrix must be symmetric (distance(i, j) == distance(j, i)).")
        
    # Check if the diagonal is all zeroes
    if not np.allclose(np.diag(matrix), 0, atol=1e-5):
        raise ValueError("Self-distances (diagonal values) must be zero.")
        
    # Build NetworkX graph
    G = nx.Graph()
    
    # Add nodes mapped to integer indices
    for i in range(num_nodes):
        G.add_node(i)
        
    # Add weighted edges between all pairs (excluding self loops)
    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            G.add_edge(i, j, weight=matrix[i, j])
            
    # Create the TSP instance from the graph
    tsp_instance = Tsp(G)
    
    # Map from index to original CSV label
    index_to_name = {i: str(name) for i, name in enumerate(node_names)}
    
    return tsp_instance, index_to_name
