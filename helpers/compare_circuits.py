from qiskit_experiments.library import QuantumVolume
import pandas as pd


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
    active = sorted({qc.find_bit(q).index for inst in qc.data for q in inst.qubits})

    return {
        "depth": qc.depth(),
        "size": qc.size(),
        "active_qubits": len(active),
        "num_nonlocal_gates": qc.num_nonlocal_gates(),
        "two_qubit_gates": _two_qubit_gate_count(qc),
        "measure_ops": counts.get("measure", 0),
        "swap_ops": counts.get("swap", 0),
        "cx_ops": counts.get("cx", 0),
        "ecr_ops": counts.get("ecr", 0),
        "cz_ops": counts.get("cz", 0),
        "counts": counts,
    }


def compare_circuits(backend, ideal_backend, subset, seed):
    subset = tuple(subset)

    experiments = {
        "optimised": _make_qv(ideal_backend, subset, seed),
        "regular": _make_qv(ideal_backend, subset, seed),
    }

    for exp in experiments.values():
        exp.set_run_options(shots=1)

    _set_opts(experiments["optimised"], backend.coupling_map, "sabre", "sabre", 3, seed)
    _set_opts(experiments["regular"],   backend.coupling_map, "trivial", "basic", 0, seed)

    rows = []

    for label, exp in experiments.items():
        qc = exp._transpiled_circuits()[0]

        row = {"variant": label}
        row.update(_collect_stats(qc))
        rows.append(row)

    return pd.DataFrame(rows)
