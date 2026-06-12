import argparse
import sys
import os
from src.problem import generate_synthetic_problem, load_custom_problem
from src.qaoa_solver import solve_tsp_qaoa
from src.visualization import plot_tsp_route

def main():
    parser = argparse.ArgumentParser(
        description="Supply Chain Route Optimization using Qiskit QAOA"
    )
    parser.add_argument(
        "--nodes",
        type=int,
        default=6,
        help="Number of locations (nodes) for the synthetic graph (default: 6)"
    )
    parser.add_argument(
        "--data-file",
        type=str,
        default=None,
        help="Path to a symmetric distance matrix CSV file (overrides --nodes)"
    )
    parser.add_argument(
        "--use-ibmq",
        action="store_true",
        help="Execute the QAOA circuit on an IBM Quantum backend (requires IBMQ_TOKEN env var)"
    )
    parser.add_argument(
        "--reps",
        type=int,
        default=1,
        help="Number of QAOA circuit layers / reps (default: 1)"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("        SUPPLY CHAIN ROUTE OPTIMIZATION WITH QAOA        ")
    print("=" * 60)
    
    # 1. Load or generate TSP instance
    if args.data_file:
        print(f"Loading custom distance matrix from: {args.data_file}")
        if not os.path.exists(args.data_file):
            print(f"Error: Data file not found: {args.data_file}")
            sys.exit(1)
        try:
            tsp_instance, index_to_name = load_custom_problem(args.data_file)
        except Exception as e:
            print(f"Error loading custom problem: {e}")
            sys.exit(1)
    else:
        print(f"Generating synthetic graph with {args.nodes} nodes...")
        try:
            tsp_instance, index_to_name = generate_synthetic_problem(args.nodes)
        except Exception as e:
            print(f"Error generating synthetic problem: {e}")
            sys.exit(1)
            
    num_nodes = len(index_to_name)
    print(f"Problem Size: {num_nodes} nodes (requires {num_nodes ** 2} qubits)")
    print("-" * 60)
    
    # 2. Solve the problem using QAOA
    print("Starting QAOA solver...")
    print("Please wait, executing the hybrid optimization loop...")
    try:
        path, distance, status_msg = solve_tsp_qaoa(
            tsp_instance=tsp_instance,
            use_ibmq=args.use_ibmq,
            reps=args.reps
        )
    except Exception as e:
        print(f"\nOptimization Failed: {e}")
        sys.exit(1)
        
    print("-" * 60)
    print("                      SOLVER RESULTS                     ")
    print("-" * 60)
    print(f"Status: {status_msg}")
    
    # Format and print the optimal path
    path_names = [index_to_name[idx] for idx in path]
    # Add start node to the end to close the cycle
    path_names.append(path_names[0])
    path_str = " -> ".join(path_names)
    
    print(f"Optimized Route: {path_str}")
    print(f"Total Distance:  {distance:.2f}")
    print("-" * 60)
    
    # 3. Visualize and save route
    save_filename = "route_optimized.png"
    print(f"Generating route visualization plot...")
    plot_tsp_route(
        tsp_instance=tsp_instance,
        path=path,
        index_to_name=index_to_name,
        title=f"Optimized Route (Dist: {distance:.2f})",
        save_path=save_filename
    )
    print("=" * 60)

if __name__ == "__main__":
    main()
