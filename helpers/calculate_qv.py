from qiskit_experiments.library import QuantumVolume
from qiskit_aer import AerSimulator
import pandas as pd


def run_qv_until_fail(backend, max_n=10, shots=100, trials=100, seed=42, optimised=True):
    ideal_backend = AerSimulator(method="statevector", device="GPU")

    rows = []
    n = 2

    while n <= max_n:
        print(f"Running QV for n = {n}")

        exp = QuantumVolume(
            physical_qubits=list(range(n)),
            trials=trials,
            seed=seed,
            simulation_backend=ideal_backend,
        )

        exp.set_run_options(shots=shots)

        if optimised:
            exp.set_transpile_options(
                coupling_map=backend.coupling_map,
                layout_method="sabre",
                routing_method="sabre",
                optimization_level=3,
                seed_transpiler=seed,
                num_processes=0,
            )
        else:
            exp.set_transpile_options(
                coupling_map=backend.coupling_map,
                layout_method="trivial",
                routing_method="basic",
                optimization_level=0,
                seed_transpiler=seed,
                num_processes=0,
            )

        exp_data = exp.run(backend, backend_run=True).block_for_results()

        df = exp_data.analysis_results(dataframe=True)
        hop_row = df[df["name"] == "mean_HOP"].iloc[0]

        mean_hop = hop_row["value"].nominal_value
        hop_err  = hop_row["value"].std_dev

        lower = mean_hop - 2 * hop_err

        rows.append({
            "n": n,
            "mean_HOP": mean_hop,
            "std_HOP": hop_err,
            "lower": lower,
            "passes": lower >= 2/3,
            "optimised": optimised
        })

        n += 1

    return pd.DataFrame(rows)