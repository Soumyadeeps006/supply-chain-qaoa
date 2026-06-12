import os
from typing import List, Tuple, Dict
from qiskit.primitives import StatevectorSampler as LocalSampler
from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA
from qiskit_optimization.problems import QuadraticProgram
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit_optimization.applications import Tsp

def solve_tsp_qaoa(
    tsp_instance: Tsp, 
    use_ibmq: bool = False, 
    reps: int = 1
) -> Tuple[List[int], float, str]:
    """
    Solves the TSP problem using Qiskit's QAOA.
    
    Args:
        tsp_instance: The Qiskit Tsp application instance.
        use_ibmq: If True, attempts to run on IBM Quantum backend.
        reps: The number of QAOA ansatz repetitions (depth p).
        
    Returns:
        A tuple of (path as list of node indices, route distance, status message).
    """
    # 1. Convert TSP instance to QuadraticProgram
    qp = tsp_instance.to_quadratic_program()
    
    # 2. Set up Sampler primitive based on backend selection
    if use_ibmq:
        token = os.environ.get("IBMQ_TOKEN")
        if not token:
            print("Warning: IBMQ_TOKEN environment variable not found. Falling back to local simulator.")
            sampler = LocalSampler()
            status_msg = "Solved locally (IBMQ_TOKEN missing)"
        else:
            try:
                from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as IBMSampler
                
                # Authenticate and setup service
                # Try to load existing or save new account
                try:
                    service = QiskitRuntimeService(channel="ibm_quantum", token=token)
                except Exception:
                    # If already saved/configured, initialize without token
                    service = QiskitRuntimeService()
                
                # Retrieve least busy backend
                backend = service.least_busy(operational=True, simulator=True)
                print(f"Connected to IBM Quantum backend: {backend.name}")
                
                sampler = IBMSampler(backend=backend)
                status_msg = f"Solved on IBM Quantum backend: {backend.name}"
            except Exception as e:
                print(f"Warning: Failed to connect to IBM Quantum backend ({e}). Falling back to local simulator.")
                sampler = LocalSampler()
                status_msg = f"Solved locally (IBM Quantum failure: {e})"
    else:
        sampler = LocalSampler()
        status_msg = "Solved locally (simulator)"
        
    # 3. Setup QAOA with classical COBYLA optimizer
    optimizer = COBYLA(maxiter=100)
    qaoa = QAOA(sampler=sampler, optimizer=optimizer, reps=reps)
    
    # 4. Use MinimumEigenOptimizer to solve the QuadraticProgram
    meo = MinimumEigenOptimizer(qaoa)
    result = meo.solve(qp)
    
    # 5. Interpret the binary result back to TSP path
    # tsp_instance.interpret returns path as list of node indices
    try:
        path = tsp_instance.interpret(result)
        
        # Calculate distance
        distance = calculate_path_distance(path, tsp_instance)
    except Exception as e:
        # Fallback if interpret fails (e.g. constraints not satisfied perfectly)
        # We can extract the path from variables directly or raise
        print(f"Error interpreting result: {e}")
        raise ValueError(f"Could not find a valid TSP path from QAOA result. Details: {result.prettyprint()}")
        
    return path, distance, status_msg

def calculate_path_distance(path: List[int], tsp_instance: Tsp) -> float:
    """
    Helper to calculate total distance of a given TSP path.
    """
    g = tsp_instance.graph
    distance = 0.0
    for i in range(len(path)):
        u = path[i]
        v = path[(i + 1) % len(path)]
        distance += g[u][v]['weight']
    return distance
