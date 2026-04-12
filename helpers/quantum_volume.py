from qiskit_experiments.library import QuantumVolume

def quantum_volume(backend, ideal_backend, subset, shots, trials, seed):
    '''Runs the Quantum Volume experiment for a 
    given subset of qubits and returns the results.'''

    exp = QuantumVolume(
        physical_qubits=list(subset),
        trials=trials,
        seed=seed,
        simulation_backend=ideal_backend,
    )

    exp.set_run_options(shots=shots)

    exp.set_transpile_options(
        coupling_map=backend.coupling_map,
        layout_method="trivial",
        routing_method="basic",
        optimization_level=0,
        seed_transpiler=seed,
        num_processes=0,
    )

    return exp.run(backend).block_for_results()


# def induced_submap_physical(full_coupling_map, subset):
#     subset = set(subset)
#     edges = [(a, b) for a, b in full_coupling_map if a in subset and b in subset]
#     return CouplingMap(edges)


def quantum_volume_optimised(backend, ideal_backend, subset, shots, trials, seed):
    '''Uses "sabre" layout and routing methods to run the QV experiment 
    with more aggressive transpilation as well as optimisation.'''

    exp = QuantumVolume(
        physical_qubits=list(subset),
        trials=trials,
        seed=seed,
        simulation_backend=ideal_backend,
    )

    exp.set_run_options(shots=shots)

    # sub_cmap = induced_submap_physical(backend.coupling_map, subset)

    exp.set_transpile_options(
        coupling_map=backend.coupling_map,
        layout_method="sabre", # trivial
        routing_method="sabre", # basic
        optimization_level=3, # 0
        seed_transpiler=seed,
        num_processes=0,
    )

    return exp.run(backend).block_for_results()

