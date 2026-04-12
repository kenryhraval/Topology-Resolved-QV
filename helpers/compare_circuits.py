from qiskit_experiments.library import QuantumVolume
from qiskit.transpiler import CouplingMap
import pandas as pd


def induced_submap_physical(full_coupling_map, subset):
    subset = set(subset)
    edges = [(a, b) for a, b in full_coupling_map if a in subset and b in subset]
    return CouplingMap(edges)


def _make_qv(ideal_backend, subset, seed):
    return QuantumVolume(
        physical_qubits=list(subset),
        trials=1,
        seed=seed,
        simulation_backend=ideal_backend,
    )


def _set_opts(exp, coupling_map, layout_method, routing_method, optimization_level, seed):
    exp.set_transpile_options(
        coupling_map=coupling_map,
        layout_method=layout_method,
        routing_method=routing_method,
        optimization_level=optimization_level,
        seed_transpiler=seed,
        num_processes=0,
    )


def _two_qubit_gate_count(qc):
    return sum(1 for inst in qc.data if len(inst.qubits) == 2)


def _collect_stats(qc):
    counts = dict(qc.count_ops())

    return {
        "depth": qc.depth(),
        "size": qc.size(),
        "width": qc.width(),
        "num_nonlocal_gates": qc.num_nonlocal_gates(),
        "two_qubit_gates": _two_qubit_gate_count(qc),
        "measure_ops": counts.get("measure", 0),
        "swap_ops": counts.get("swap", 0),
        "cx_ops": counts.get("cx", 0),
        "ecr_ops": counts.get("ecr", 0),
        "cz_ops": counts.get("cz", 0),
        "counts": counts,
    }


def compare_circuits(backend, ideal_backend, subset, shots, trials, seed):
    subset = tuple(subset)
    sub_cmap = induced_submap_physical(backend.coupling_map, subset)

    experiments = {
        "induced_optimised": _make_qv(ideal_backend, subset, trials, seed),
        "induced_regular": _make_qv(ideal_backend, subset, trials, seed),
        "full_optimised": _make_qv(ideal_backend, subset, trials, seed),
        "full_regular": _make_qv(ideal_backend, subset, trials, seed),
    }

    for exp in experiments.values():
        exp.set_run_options(shots=shots)

    _set_opts(experiments["induced_optimised"], sub_cmap, "sabre", "sabre", 3, seed)
    _set_opts(experiments["induced_regular"],   sub_cmap, "trivial", "basic", 0, seed)
    _set_opts(experiments["full_optimised"],    backend.coupling_map, "sabre", "sabre", 3, seed)
    _set_opts(experiments["full_regular"],      backend.coupling_map, "trivial", "basic", 0, seed)

    rows = []

    for label, exp in experiments.items():
        qc = exp._transpiled_circuits()[0]

        row = {"variant": label}
        row.update(_collect_stats(qc))
        rows.append(row)

    df = pd.DataFrame(rows)
    return df

